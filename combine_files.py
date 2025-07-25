import os
from datetime import datetime

source_folder = r"C:\Users\Edgar.000\Documents\____Trading strategies\Crypto_trading"
output_folder = r"C:\Users\Edgar.000\Desktop"

#import os
from datetime import datetime

# 🔧 Change this to the folder with your .txt files

# 📂 Destination file name with today's date
today = datetime.today().strftime('%Y-%m-%d')
output_file = f"combined_{today}.txt"

# 📦 Full path for output
output_path = os.path.join(source_folder, output_file)

# 📄 Combine contents
with open(output_path, 'w', encoding='utf-8') as outfile:
    for filename in os.listdir(source_folder):
        if filename.endswith(".txt") and filename != output_file:
            file_path = os.path.join(source_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
                outfile.write(f"\n--- {filename} ---\n")
                outfile.write(content + "\n")

print(f"✅ All .txt files combined and saved as: {output_file}")
