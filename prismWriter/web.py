import os
import subprocess

def main():
    #run the streamlit app, this will block until the app is closed
    subprocess.run(['streamlit', 'run', 'prismWriter/streamlit_app.py'])
if __name__ == "__main__":
    main()