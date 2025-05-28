"""
Concept extraction utilities
"""

def get_concept_extraction_prompt(concept_topic, subject, language="fr"):
    """Generate the appropriate prompt for concept extraction in the specified language"""
    if language == "fr":
        return get_french_concept_extraction_prompt(concept_topic, subject)
    else:
        return get_english_concept_extraction_prompt(concept_topic, subject)


def get_french_concept_extraction_prompt(concept_topic, subject):
    """Generate French prompt for concept extraction"""
    if concept_topic:
        prompt = f"""
Extrayez les 7-10 concepts {subject} les plus importants sur '{concept_topic}' des documents.
Pour chaque concept incluez :
1. Définition
2. Caractéristiques clés
3. Exemples spécifiques à {subject}
4. Applications pratiques

Formatez comme ceci :

### Concepts clés en {subject.capitalize()} : {concept_topic}

1. **[Nom du concept]** : [Définition/explication]
   - **Caractéristiques** : [Liste des caractéristiques]
   - **Exemple** : [Exemple pertinent]
   - **Application** : [Comment c'est utilisé en {subject}]

2. **[Nom du concept]** : [Définition/explication]
   ...
"""
    else:
        prompt = f"""
Extrayez les 10-15 concepts {subject} les plus importants de l'ensemble du document.
Organisez par thèmes principaux avec le contexte spécifique à {subject}.

Formatez comme ceci :

### Concepts clés du document en {subject.capitalize()}

#### [Thème principal 1]
1. [Concept] - [Explication avec contexte {subject}]
2. [Concept] - [Explication avec contexte {subject}]

#### [Thème principal 2]
...
"""
    
    return prompt


def get_english_concept_extraction_prompt(concept_topic, subject):
    """Generate English prompt for concept extraction"""
    if concept_topic:
        prompt = f"""
Extract the 7-10 most important {subject} concepts on '{concept_topic}' from the documents.
For each concept include:
1. Definition
2. Key characteristics
3. Examples specific to {subject}
4. Practical applications

Format as follows:

### Key Concepts in {subject.capitalize()}: {concept_topic}

1. **[Concept Name]**: [Definition/explanation]
   - **Characteristics**: [List of characteristics]
   - **Example**: [Relevant example]
   - **Application**: [How it's used in {subject}]

2. **[Concept Name]**: [Definition/explanation]
   ...
"""
    else:
        prompt = f"""
Extract the 10-15 most important {subject} concepts from the entire document.
Organize by main themes with context specific to {subject}.

Format as follows:

### Key Concepts from the Document in {subject.capitalize()}

#### [Main Theme 1]
1. [Concept] - [Explanation with {subject} context]
2. [Concept] - [Explanation with {subject} context]

#### [Main Theme 2]
...
"""
    
    return prompt
