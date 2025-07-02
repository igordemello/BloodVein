import json
import os
from datetime import datetime

class SaveManager:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def get_save_files(self):
        return [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
    
    def create_save(self, game_state):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(self.save_dir, f"save_{timestamp}.json")
        self.save_game(game_state, save_path)
        return save_path
    
    def save_game(self, game_state, save_path):
        with open(save_path, 'w') as f:
            json.dump(game_state, f, indent=4)
    
    def load_game(self, save_path):
        with open(save_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def generate_game_state(player, andar, sala_atual):
        return {
            'player': player.get_save_data(),
            'map': andar.get_save_data(),
            'sala': sala_atual.get_save_data() if sala_atual else None,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }