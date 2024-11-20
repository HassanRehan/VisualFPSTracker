import subprocess

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    # Start both scripts concurrently
    process1 = subprocess.Popen(["python", "screenCNN.py"])
    process2 = subprocess.Popen(["python", "screenOCR.py"])

    # Wait for both processes to complete
    process1.wait()
    process2.wait()