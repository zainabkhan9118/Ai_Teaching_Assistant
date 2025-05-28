"""
OpenAI integration utilities
"""

import os
import streamlit as st
import openai


def generate_questions(question_type, num_questions, topic, subject, difficulty, relevant_content, llm_model_name, language="fr"):
    """Generate questions based on configuration and content"""
    if language == "fr":
        return generate_french_questions(question_type, num_questions, topic, subject, difficulty, relevant_content, llm_model_name)
    else:
        return generate_english_questions(question_type, num_questions, topic, subject, difficulty, relevant_content, llm_model_name)


def generate_french_questions(question_type, num_questions, topic, subject, difficulty, relevant_content, llm_model_name):
    """Generate questions in French"""
    if question_type == "QCM":
        prompt = f"""
Générez {num_questions} QCM de niveau {difficulty.lower()} sur '{topic}' en {subject}.
Basez-vous strictement sur ce contenu : {relevant_content}

Formattez chaque question EXACTEMENT comme ceci :

### Question [N]

**[Q].** [Énoncé de la question]

- **A)** [Option A]
- **B)** [Option B]
- **C)** [Option C]
- **D)** [Option D]

**Réponse :** [Lettre correcte]
**Explication :** [Explication de 1-2 phrases avec référence aux concepts de {subject}]

---
"""
    elif question_type == "Vrai/Faux":
        prompt = f"""
Générez {num_questions} questions Vrai/Faux sur '{topic}' en {subject}.
Incluez des explications et référez-vous au contenu.

Formattez EXACTEMENT comme ceci :

### Question [N]

**[Q].** [Énoncé]

**Réponse :** Vrai/Faux
**Explication :** [Explication avec référence aux supports de {subject}]

---
"""
    elif question_type in ["Calcul", "Analyse de cas"]:
        prompt = f"""
Générez {num_questions} problèmes de type {question_type.lower()} sur '{topic}' en {subject}.
Incluez des solutions détaillées.

Formattez EXACTEMENT comme ceci :

### Problème [N]

**[Q].** [Énoncé du problème]

**Solution :** 
[Solution étape par étape avec raisonnement spécifique à {subject}]

**Point clé :**
[Principale notion à retenir]

---
"""
    else:
        prompt = f"""
Générez {num_questions} questions de type {question_type.lower()} sur '{topic}' en {subject}.
Incluez des réponses détaillées.

Formattez EXACTEMENT comme ceci :

### Question [N]

**[Q].** [Question]

**Réponse :** 
[Réponse détaillée avec référence aux supports de {subject}]

---
"""
    
    # Generate questions
    response = openai.chat.completions.create(
        model=llm_model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    return response.choices[0].message.content


def generate_english_questions(question_type, num_questions, topic, subject, difficulty, relevant_content, llm_model_name):
    """Generate questions in English"""
    # Map French question types to English types
    question_type_map = {
        "QCM": "Multiple Choice",
        "Vrai/Faux": "True/False",
        "Calcul": "Calculation",
        "Analyse de cas": "Case Analysis"
    }
    
    # Use mapped question type or original if not in map
    eng_question_type = question_type_map.get(question_type, question_type)
    
    # Map difficulty levels
    difficulty_map = {
        "Facile": "Easy",
        "Moyen": "Medium",
        "Difficile": "Hard"
    }
    eng_difficulty = difficulty_map.get(difficulty, "Medium")
    
    if eng_question_type == "Multiple Choice":
        prompt = f"""
Generate {num_questions} multiple-choice questions at {eng_difficulty.lower()} level on '{topic}' in {subject}.
Base your questions strictly on this content: {relevant_content}

Format each question EXACTLY as follows:

### Question [N]

**[Q].** [Question statement]

- **A)** [Option A]
- **B)** [Option B]
- **C)** [Option C]
- **D)** [Option D]

**Answer:** [Correct letter]
**Explanation:** [1-2 sentence explanation with reference to {subject} concepts]

---
"""
    elif eng_question_type == "True/False":
        prompt = f"""
Generate {num_questions} True/False questions on '{topic}' in {subject}.
Include explanations and refer to the content.

Format EXACTLY as follows:

### Question [N]

**[Q].** [Statement]

**Answer:** True/False
**Explanation:** [Explanation with reference to {subject} material]

---
"""
    elif eng_question_type in ["Calculation", "Case Analysis"]:
        prompt = f"""
Generate {num_questions} {eng_question_type.lower()} problems on '{topic}' in {subject}.
Include detailed solutions.

Format EXACTLY as follows:

### Problem [N]

**[Q].** [Problem statement]

**Solution:** 
[Step-by-step solution with reasoning specific to {subject}]

**Key Point:**
[Main concept to remember]

---
"""
    else:
        prompt = f"""
Generate {num_questions} {eng_question_type.lower()} questions on '{topic}' in {subject}.
Include detailed answers.

Format EXACTLY as follows:

### Question [N]

**[Q].** [Question]

**Answer:** 
[Detailed answer with reference to {subject} material]

---
"""
    
    # Generate questions
    response = openai.chat.completions.create(
        model=llm_model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    return response.choices[0].message.content
