import subprocess
import pandas as pd

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":

    print(">>>Starting both scripts concurrently...")
    # Start both scripts concurrently
    process1 = subprocess.Popen(["python", "screenCNN.py"])
    process2 = subprocess.Popen(["python", "screenOCR_CV.py"])
    # Wait for both processes to complete
    process1.wait()
    process2.wait()
    print("\---- Both scripts have completed.")


    print(">>> Starting merge script...")
    # Read the Excel files
    cnn_df = pd.read_excel('cnn_data.xlsx')
    ocr_df = pd.read_excel('ocr_data.xlsx')
    # Merge the dataframes on the "Elapsed Time (s)" column
    merged_df = pd.merge(cnn_df, ocr_df, on='Elapsed Time (s)', suffixes=('_cnn', '_ocr'))
    # Save the merged dataframe to a new Excel file
    merged_df.to_excel('merged_data.xlsx', index=False)
    print("\----Merge script has completed.")


    print(">>> Starting post-game info script...")
    process3 = subprocess.Popen(["python", "postGameInfo.py"])
    print("\---- Post-game info script has completed.")