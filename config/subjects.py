"""
Subject-specific configurations for different academic disciplines
"""

# Subject-specific configurations in French
SUBJECT_CONFIGS_FR = {
    "économie": {
        "description": "Théories économiques, modèles et applications pratiques",
        "guidance": """
        - Utilisez toujours les principes économiques comme l'offre/demande, l'élasticité, le coût d'opportunité
        - Utilisez des graphiques appropriés pour expliquer les concepts
        - Différenciez les concepts de micro et macroéconomie
        - Référencez les théories des économistes clés
        - Pour les calculs, montrez les formules étape par étape
        """,
        "examples": """
        **Exemple Q:** Expliquez l'élasticité-prix de la demande ?
        **Exemple A:** 
        **L'élasticité-prix de la demande** mesure comment la quantité demandée réagit aux changements de prix...
        
        Formule : 
        ```
        PED = (%Δ Quantité Demandée) / (%Δ Prix)
        ```
        
        Types :
        - Élastique (PED > 1)
        - Inélastique (PED < 1)
        - Élasticité unitaire (PED = 1)
        
        **Exemple concret :** L'essence a souvent une demande inélastique...
        """,
        "question_types": {
            "QCM": "Inclure des questions sur les modèles économiques et l'interprétation des graphiques",
            "Vrai/Faux": "Se concentrer sur les principes économiques et les idées fausses courantes",
            "Calcul": "Inclure des problèmes avec des formules économiques et des solutions étape par étape"
        }
    },
    "marketing": {
        "description": "Stratégies marketing, comportement du consommateur et analyse de campagnes",
        "guidance": """
        - Référencez le cadre des 4P (Produit, Prix, Place, Promotion)
        - Utilisez des exemples de marketing modernes
        - Différenciez le marketing B2B et B2C
        - Incluez des considérations sur le marketing digital
        - Référencez des études de cas lorsque cela est approprié
        """,
        "examples": """
        **Exemple Q:** Qu'est-ce qui fait une campagne marketing efficace ?
        **Exemple A:** Les éléments clés incluent :
        1. **Définition claire du public cible**
        2. **Articulation de la proposition de valeur**
        3. **Intégration multi-canal**
        4. **KPI mesurables**
        
        **Exemple :** La campagne 'Think Different' d'Apple a réussi parce que...
        """,
        "question_types": {
            "QCM": "Questions sur les cadres marketing et les études de cas",
            "Vrai/Faux": "Principes marketing et comportement du consommateur",
            "Analyse de cas": "Fournir des mini études de cas à analyser"
        }
    },
    "finance": {
        "description": "Analyse financière, évaluation et stratégies d'investissement",
        "guidance": """
        - Utilisez la terminologie financière appropriée
        - Montrez les calculs étape par étape
        - Différenciez la finance d'entreprise et les investissements
        - Référencez les ratios et métriques financiers clés
        - Utilisez des exemples numériques réalistes
        """,
        "examples": """
        **Exemple Q:** Comment calculez-vous la VAN ?
        **Exemple A:**
        **La Valeur Actuelle Nette (VAN)** calcule la valeur actuelle des flux de trésorerie futurs :
        
        Formule :
        ```
        VAN = Σ [CFₜ / (1+r)ᵗ] - Investissement Initial
        ```
        
        Où :
        - CFₜ = Flux de trésorerie à la période t
        - r = Taux d'actualisation
        - t = Période
        
        **Exemple :** Pour un projet avec un investissement initial de 100€...
        """,
        "question_types": {
            "QCM": "Questions sur les formules financières et l'analyse des ratios",
            "Calcul": "Problèmes financiers nécessitant des solutions étape par étape",
            "Analyse de scénario": "Présenter des scénarios d'investissement à évaluer"
        }
    }
}
