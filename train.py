import time
import sys
import torch.multiprocessing as mp
from ai import MctsValueAgent

NUM_WORKERS = 8
NUM_GAMES = 1000

def worker_self_play(worker_id, model_weights, task_queue, result_queue):
    """
    Runs in each worker process.
    Plays games using a local model copy.
    """
    print(f"[Worker {worker_id}] starting...")

    # Build agent with same architecture
    agent = MctsValueAgent(time_limit=1.0)

    # Load initial weights
    agent.model.load_state_dict(model_weights)

    while True:
        task = task_queue.get()
        if task == "STOP":
            break

        if task == "PLAY":
            # Play 1 game
            game_data = agent.generate_self_play_game()  # returns list of (state, outcome)

            # send results back
            result_queue.put(game_data)

        elif isinstance(task, dict) and "weights" in task:
            # Update model on worker
            agent.model.load_state_dict(task["weights"])
            print(f"[Worker {worker_id}] model updated.")

    print(f"[Worker {worker_id}] exiting.")


def main():
    agent = MctsValueAgent(time_limit=1.0, c=1.414)
    agent.model.share_memory()  # required for MP

    manager = mp.Manager()
    task_queue = manager.Queue()
    result_queue = manager.Queue()

    # Launch workers
    workers = []
    for wid in range(NUM_WORKERS):
        p = mp.Process(
            target=worker_self_play,
            args=(wid, agent.model.state_dict(), task_queue, result_queue)
        )
        p.start()
        workers.append(p)

    print("[Trainer] Starting self-play...")
    start_time = time.time()

    games_collected = 0

    while True:
        # Ask workers to produce games
        for _ in range(NUM_WORKERS):
            task_queue.put("PLAY")

        # Collect results
        for _ in range(NUM_WORKERS):
            game_data = result_queue.get()  # list of (state, outcome)
            agent.add_to_replay_buffer(game_data)
            games_collected += 1

        # Train periodically
        if games_collected % 24 == 0:
            agent.train_from_replay()
            print(f"[Trainer] {games_collected} games collected. Updated model. Sending weights to workers...")

            # Broadcast updated weights
            updated = agent.model.state_dict()
            for _ in range(NUM_WORKERS):
                task_queue.put({"weights": updated})

            agent._save_model()

        # Optional: stop condition
        if games_collected >= NUM_GAMES:
            break

    # Stop workers
    for _ in range(NUM_WORKERS):
        task_queue.put("STOP")
    for p in workers:
        p.join()

    end_time = time.time()
    print(f"[Trainer] Self-play completed. {games_collected} games in {(end_time - start_time)/60:.2f} mins")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py train.py NUM_GAMES")
        sys.exit(1)
    NUM_GAMES = int(sys.argv[1])
    mp.set_start_method("spawn")  # required on Windows
    main()
