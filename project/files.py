import os

def print_tree(path, indent=""):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            print(indent + f"├── {item}/")
            print_tree(item_path, indent + "│   ")
        else:
            print(indent + f"├── {item}")

if __name__ == "__main__":
    root_folder = "/path/to/your/folder"
    print(root_folder)
    print_tree(root_folder)