from flask import Flask, render_template, request, jsonify
import csv

app = Flask(__name__)

def read_dictionary(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        dictionary = [row[0] for row in reader if row]
    return dictionary

filename = 'dict.csv'  
dictionary = read_dictionary(filename)

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def spell_check(word):
    suggestions = [w for w in dictionary if levenshtein_distance(word, w) <= 2]
    return suggestions

def backtrack_autocorrect(word):
    def backtrack(word, depth):
        if depth == 0:
            return word
        suggestions = spell_check(word)
        if suggestions:
            for suggestion in suggestions:
                corrected_word = backtrack(suggestion, depth - 1)
                if corrected_word:
                    return corrected_word
        return None
    
    return backtrack(word, 2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_suggestions', methods=['POST'])
def search_word():
    word = request.form['word']
    if word in dictionary:
        return jsonify({'result': f"Meaning of '{word}'"})
    else:
        suggestions = spell_check(word)
        if suggestions:
            filtered_suggestions = [suggestion for suggestion in suggestions if suggestion.startswith(word[0])]
            if filtered_suggestions:
                return jsonify({'result': f"No word found. Did you mean: {', '.join(filtered_suggestions)}?"})
            else:
                return jsonify({'result': f"No word found. Did you mean: {', '.join(suggestions)}?"})
        else:
            corrected_word = backtrack_autocorrect(word)
            if corrected_word:
                return jsonify({'result': f"'{word}' not found in dictionary. Did you mean: {corrected_word}?"})
            else:
                return jsonify({'result': f"'{word}' not found in dictionary. No suggestions available."})

@app.route('/delete_word', methods=['POST'])
def delete_word():
    word = request.form['word']
    if word in dictionary:
        dictionary.remove(word)
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for word in dictionary:
                writer.writerow([word])
        return jsonify({'result': "Word deleted successfully!"})
    else:
        return jsonify({'error': f"'{word}' not found in dictionary."})

@app.route('/display_dictionary', methods=['GET'])
def display_dictionary():
    return jsonify({'dictionary': dictionary})

if __name__ == '__main__':
    app.run(debug=True)
