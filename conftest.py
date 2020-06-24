import os
import sys

inserted_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, inserted_path)
