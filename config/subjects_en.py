"""
English subject configurations for different academic disciplines
"""

# Subject-specific configurations in English
SUBJECT_CONFIGS_EN = {
    "economics": {
        "description": "Economic theories, models, and practical applications",
        "guidance": """
        - Always use economic principles like supply/demand, elasticity, opportunity cost
        - Use appropriate graphs to explain concepts
        - Differentiate between micro and macroeconomic concepts
        - Reference theories from key economists
        - For calculations, show formulas step-by-step
        """,
        "examples": """
        **Example Q:** Explain price elasticity of demand?
        **Example A:** 
        **Price elasticity of demand** measures how quantity demanded responds to price changes...
        
        Formula: 
        ```
        PED = (%Δ Quantity Demanded) / (%Δ Price)
        ```
        
        Types:
        - Elastic (PED > 1)
        - Inelastic (PED < 1)
        - Unitary elasticity (PED = 1)
        
        **Concrete example:** Gasoline often has inelastic demand...
        """,
        "question_types": {
            "Multiple Choice": "Include questions on economic models and graph interpretation",
            "True/False": "Focus on economic principles and common misconceptions",
            "Calculation": "Include problems with economic formulas and step-by-step solutions"
        }
    },
    "marketing": {
        "description": "Marketing strategies, consumer behavior, and campaign analysis",
        "guidance": """
        - Reference the 4P framework (Product, Price, Place, Promotion)
        - Use modern marketing examples
        - Differentiate B2B and B2C marketing
        - Include digital marketing considerations
        - Reference case studies when appropriate
        """,
        "examples": """
        **Example Q:** What makes an effective marketing campaign?
        **Example A:** Key elements include:
        1. **Clear target audience definition**
        2. **Value proposition articulation** 
        3. **Multi-channel integration**
        4. **Measurable KPIs**
        
        **Example:** Apple's 'Think Different' campaign succeeded because...
        """,
        "question_types": {
            "Multiple Choice": "Questions on marketing frameworks and case studies",
            "True/False": "Marketing principles and consumer behavior",
            "Case Analysis": "Provide mini case studies to analyze"
        }
    },
    "finance": {
        "description": "Financial analysis, valuation, and investment strategies",
        "guidance": """
        - Use appropriate financial terminology
        - Show calculations step-by-step
        - Differentiate corporate finance and investments
        - Reference key financial ratios and metrics
        - Use realistic numerical examples
        """,
        "examples": """
        **Example Q:** How do you calculate NPV?
        **Example A:**
        **Net Present Value (NPV)** calculates the present value of future cash flows:
        
        Formula:
        ```
        NPV = Σ [CFₜ / (1+r)ᵗ] - Initial Investment
        ```
        
        Where:
        - CFₜ = Cash flow in period t
        - r = Discount rate
        - t = Period
        
        **Example:** For a project with an initial investment of $100...
        """,
        "question_types": {
            "Multiple Choice": "Questions on financial formulas and ratio analysis",
            "Calculation": "Financial problems requiring step-by-step solutions",
            "Scenario Analysis": "Present investment scenarios to evaluate"
        }
    }
}
