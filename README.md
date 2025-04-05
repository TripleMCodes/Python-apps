📝 Note Worthy
Note Worthy is a sleek, minimalist note-taking app built with PySide6 (Qt for Python), designed to be both functional and aesthetic. Whether you're jotting down poetry or Python, it’s got your back with features like:

💡 Real-time word count

📚 WordNet dictionary integration

🎨 Toggleable dark/light mode

✂️ Basic editing functions (copy, cut, paste, undo, redo, clear)

💾 File open/save dialog

🔤 Adjustable font size

🧠 Persistence of theme and font settings via config file

⚙️ Features
Feature	Description
Word Count	Displays live word count as you type.
WordNet Dictionary	Fetches up to 3 definitions using NLTK's WordNet.
Sidebar Menu	Easily accessible controls for file I/O and theme.
Dark/Light Mode	Switch between cozy dark or clean light themes.
Font Size Control	Choose from a range of font sizes from a dropdown.
🚀 Getting Started
🔧 Requirements
To run this app, you'll need Python and the following packages:

pip install -r requirements.txt
requirements.txt 📦
PySide6
nltk
Note: The first time you run the app, it will download the WordNet corpus automatically via nltk.download('wordnet').

🏃 Running the App
python note_worthy.py
💾 Config File
User preferences like theme and font size are stored in a JSON file:

config.json

🧠 Creator
Built with caffeine and curiosity by Connor Connorson ☕🧠
(aka M.M.M.C—poet, coder, philosopher, polymath-in-progress)