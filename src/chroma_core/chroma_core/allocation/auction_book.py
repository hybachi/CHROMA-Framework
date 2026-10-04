"""
auction_book.py
Manages the state dictionary tracking for bids and distributed auctions.
"""

class AuctionBook:
    def __init__(self):
        self.bids_received = {}
        self.tasks_bid_on = set()
        self.pending_auctions = set()
        self.assigned_tasks = {}

    def record_bid(self, task_id, robot_id, score):
        if task_id not in self.bids_received:
            self.bids_received[task_id] = {}
        self.bids_received[task_id][robot_id] = score

    def get_winner(self, task_id):
        """Returns (winner_id, top_score). Defaults to ('', -1.0)"""
        all_bids = self.bids_received.get(task_id, {})
        if not all_bids:
            return "", -1.0

        # Find the highest score
        top_score = max(all_bids.values())
        
        # Find all robots that tied for the top score
        tied_robots = [rid for rid, score in all_bids.items() if score == top_score]
        
        # Break ties lexicographically
        winner_id = min(tied_robots)

        return winner_id, top_score

    def assign_task(self, task_id, robot_id):
        self.assigned_tasks[task_id] = robot_id
        self.pending_auctions.discard(task_id)

    def is_assigned(self, task_id):
        return task_id in self.assigned_tasks

    def get_assigned_robot(self, task_id):
        return self.assigned_tasks.get(task_id)

    def unassign_task(self, task_id):
        self.assigned_tasks.pop(task_id, None)

    def clear_auction_state(self, task_id):
        self.tasks_bid_on.discard(task_id)
        self.pending_auctions.discard(task_id)
        self.bids_received.pop(task_id, None)