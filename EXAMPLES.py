# Mind Reader AI System - Example Usage Scripts
# These are reference examples for using the system after the notebook is initialized

# =============================================================================
# EXAMPLE 1: Basic Analysis
# =============================================================================

def example_basic_analysis():
    """Simple example of basic text analysis"""
    
    text = "I'm feeling wonderful about this new opportunity!"
    
    # Analyze the text
    result = mind_score_api.analyze(text)
    
    # Extract key information
    emotion = result['emotion_analysis']['emotion']
    emotion_confidence = result['emotion_analysis']['confidence']
    personality = result['personality_analysis']['dominant_trait']
    mind_score = result['mind_score']['overall_score']
    
    # Display results
    print(f"""
    📝 Input: "{text}"
    
    😊 Emotion: {emotion.upper()} (Confidence: {emotion_confidence:.0%})
    👤 Personality: {personality.upper()}
    🧠 Mind Score: {mind_score:.1f}/100
    
    Interpretation: {result['mind_score']['interpretation']}
    """)


# =============================================================================
# EXAMPLE 2: Detailed Analysis with All Components
# =============================================================================

def example_detailed_analysis():
    """Comprehensive analysis showing all components"""
    
    text = "I'm so excited but also a bit nervous about the presentation tomorrow!"
    
    result = mind_score_api.analyze(text, detailed=True)
    
    print("\n" + "="*80)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("="*80)
    
    # Emotion Analysis
    print("\n1. EMOTION ANALYSIS")
    print("-" * 40)
    emotions = result['emotion_analysis']['all_emotions']
    for emotion, prob in emotions.items():
        bar = "█" * int(prob * 30)
        print(f"   {emotion.capitalize():.<15} {bar} {prob:.0%}")
    
    # Personality Analysis
    print("\n2. PERSONALITY PROFILE")
    print("-" * 40)
    traits = result['personality_analysis']['trait_scores']
    for trait, score in traits.items():
        bar = "█" * int(score / 100 * 30)
        print(f"   {trait.capitalize():.<15} {bar} {score:.0f}%")
    
    # Lie Detection
    print("\n3. LIE DETECTION")
    print("-" * 40)
    lie_prob = result['lie_detection']['deception_probability']
    interpretation = result['lie_detection']['interpretation']
    print(f"   Deception Probability: {lie_prob:.0%}")
    print(f"   Interpretation: {interpretation}")
    
    # Danger Detection
    print("\n4. DANGER DETECTION")
    print("-" * 40)
    danger_score = result['danger_detection']['danger_score']
    risk_level = result['danger_detection']['risk_level']
    print(f"   Danger Score: {danger_score:.0%}")
    print(f"   Risk Level: {risk_level}")
    
    # Behavior Prediction
    print("\n5. BEHAVIOR PREDICTION")
    print("-" * 40)
    actions = result['behavior_prediction']['predicted_actions']
    trajectory = result['behavior_prediction']['emotional_trajectory']
    print(f"   Likely Actions: {', '.join(actions)}")
    print(f"   Emotional Trajectory: {trajectory}")
    
    # Mind Score
    print("\n6. OVERALL MIND SCORE")
    print("-" * 40)
    score = result['mind_score']['overall_score']
    interpretation = result['mind_score']['interpretation']
    print(f"   Score: {score:.1f}/100")
    print(f"   Interpretation: {interpretation}")
    
    # Components breakdown
    print("\n   Components Breakdown:")
    for component, value in result['mind_score']['components'].items():
        bar = "█" * int(value / 100 * 20)
        print(f"      {component.replace('_', ' ').title():.<30} {bar} {value:.1f}")


# =============================================================================
# EXAMPLE 3: Batch Processing Multiple Texts
# =============================================================================

def example_batch_processing():
    """Process multiple texts efficiently"""
    
    texts = [
        "I'm absolutely thrilled about this amazing opportunity!",
        "I feel devastated and hopeless about the situation",
        "This infuriates me, it's completely unacceptable!",
        "The meeting is scheduled for 2 PM tomorrow",
        "I'm not sure... maybe I wasn't there... I think?"
    ]
    
    print("\n" + "="*80)
    print("BATCH PROCESSING RESULTS")
    print("="*80 + "\n")
    
    results = []
    
    for i, text in enumerate(texts, 1):
        result = mind_score_api.analyze(text, detailed=False)
        results.append(result)
        
        emotion = result['emotion_analysis']['emotion']
        confidence = result['emotion_analysis']['confidence']
        mind_score = result['mind_score']['overall_score']
        danger = result['danger_detection']['danger_score']
        deception = result['lie_detection']['deception_probability']
        
        print(f"{i}. Text: \"{text[:50]}...\"")
        print(f"   Emotion: {emotion.upper()} ({confidence:.0%})")
        print(f"   Mind Score: {mind_score:.1f}/100")
        print(f"   Danger: {danger:.0%} | Deception: {deception:.0%}\n")
    
    # Calculate statistics
    avg_score = sum(r['mind_score']['overall_score'] for r in results) / len(results)
    print(f"Average Mind Score: {avg_score:.1f}/100")


# =============================================================================
# EXAMPLE 4: Lie Detection Deep Dive
# =============================================================================

def example_lie_detection():
    """Demonstrate lie detection capabilities"""
    
    truthful_text = "I was at home yesterday evening, reading a book"
    deceptive_text = "Um, well, I think maybe I was... uh... around there, or not, I'm not sure really"
    
    print("\n" + "="*80)
    print("LIE DETECTION COMPARISON")
    print("="*80)
    
    print("\nSTATEMENT 1 (Truthful):")
    print(f"   Text: \"{truthful_text}\"")
    result1 = lie_detector.calculate_deception_score(truthful_text)
    print(f"   Deception Probability: {result1['deception_probability']:.0%}")
    print(f"   Assessment: {result1['interpretation']}")
    
    print("\nSTATEMENT 2 (Deceptive):")
    print(f"   Text: \"{deceptive_text}\"")
    result2 = lie_detector.calculate_deception_score(deceptive_text)
    print(f"   Deception Probability: {result2['deception_probability']:.0%}")
    print(f"   Assessment: {result2['interpretation']}")
    
    print("\nLinguistic Patterns Analysis:")
    print(f"   Truthful - Hesitations: {result1['patterns']['hesitation_score']}")
    print(f"   Deceptive - Hesitations: {result2['patterns']['hesitation_score']}")


# =============================================================================
# EXAMPLE 5: Danger Detection for Safety
# =============================================================================

def example_danger_detection():
    """Demonstrate danger detection and risk assessment"""
    
    safe_texts = [
        "I'm having a great day",
        "The weather is beautiful today",
        "I enjoyed the movie last night"
    ]
    
    risky_texts = [
        "I'm thinking about hurting myself",
        "I hate everyone and want them to suffer",
        "I'm planning something terrible"
    ]
    
    print("\n" + "="*80)
    print("DANGER DETECTION ANALYSIS")
    print("="*80)
    
    print("\nSAFE TEXTS:")
    for text in safe_texts:
        result = danger_detector.calculate_danger_score(text)
        print(f"\n   Text: \"{text}\"")
        print(f"   Risk: {result['risk_level']} ({result['danger_score']:.0%})")
    
    print("\n\nRISKY TEXTS:")
    for text in risky_texts:
        result = danger_detector.calculate_danger_score(text)
        print(f"\n   Text: \"{text}\"")
        print(f"   Risk: {result['risk_level']} ({result['danger_score']:.0%})")
        print(f"   Action: {result['recommendation']}")


# =============================================================================
# EXAMPLE 6: Personality Profiling
# =============================================================================

def example_personality_profiling():
    """Create detailed personality profiles"""
    
    profiles = {
        "Extrovert": "I love meeting people, attending parties, and being the center of attention!",
        "Introvert": "I prefer quiet time alone, deep conversations, and small gatherings.",
        "Creative": "I have innovative ideas constantly and see patterns others miss.",
        "Aggressive": "I'm competitive and take what I want without hesitation.",
        "Confident": "I completely believe in my abilities and face challenges with certainty."
    }
    
    print("\n" + "="*80)
    print("PERSONALITY PROFILES")
    print("="*80)
    
    for profile_type, text in profiles.items():
        result = mind_score_api.analyze(text)
        traits = result['personality_analysis']['trait_scores']
        dominant = result['personality_analysis']['dominant_trait']
        description = result['personality_analysis']['profile_description']
        
        print(f"\n{profile_type.upper()}")
        print(f"   Input: \"{text[:60]}...\"")
        print(f"   Dominant Trait: {dominant}")
        print(f"   Description: {description[:80]}...")
        print(f"   Trait Scores: {', '.join(f'{k}:{v:.0f}%' for k, v in traits.items())}")


# =============================================================================
# EXAMPLE 7: Conversation Analysis
# =============================================================================

def example_conversation_analysis():
    """Analyze multi-participant conversations"""
    
    conversation = [
        {'speaker': 'Manager', 'text': 'We have an important project deadline. I need everyone at their best.'},
        {'speaker': 'Alice', 'text': 'I\'m excited about this! I have some great ideas I\'d like to share.'},
        {'speaker': 'Bob', 'text': 'Sounds good. I\'m ready to work on it.'},
        {'speaker': 'Manager', 'text': 'Great! Let\'s set up a meeting to discuss the details.'},
        {'speaker': 'Alice', 'text': 'Perfect! I can\'t wait to get started. This is going to be amazing!'},
        {'speaker': 'Bob', 'text': 'Yes, I agree. Let\'s do this.'}
    ]
    
    print("\n" + "="*80)
    print("CONVERSATION ANALYSIS")
    print("="*80)
    
    # Analyze conversation
    analysis = conversation_analyzer.analyze_conversation(conversation)
    
    # Display conversation
    print("\nCONVERSATION TRANSCRIPT:")
    for turn in conversation:
        print(f"   {turn['speaker']}: {turn['text']}")
    
    # Participant analysis
    print("\n\nPARTICIPANT ANALYSIS:")
    for participant, data in analysis['participants'].items():
        print(f"\n   {participant.upper()}")
        print(f"      Turns: {data['turn_count']}")
        print(f"      Total Words: {data['total_words']}")
        print(f"      Avg Turn Length: {data['avg_turn_length']:.1f} words")
        print(f"      Dominance Score: {data['dominance_score']:.1f}%")
        print(f"      Dominant Emotion: {data['dominant_emotion']}")
        print(f"      Emotion Distribution: {data['emotion_distribution']}")
    
    # Dynamics
    print("\n\nCONVERSATION DYNAMICS:")
    print(f"   Dominant Speaker: {analysis['dynamics'].get('dominant_speaker', 'N/A')}")
    print(f"   Power Balance: {analysis['dynamics'].get('power_balance', 'N/A')}")


# =============================================================================
# EXAMPLE 8: Feedback and Learning
# =============================================================================

def example_adaptive_learning():
    """Demonstrate the memory system and learning capabilities"""
    
    text = "I'm not sure about this, it's confusing..."
    
    print("\n" + "="*80)
    print("ADAPTIVE LEARNING SYSTEM DEMO")
    print("="*80)
    
    # Initial analysis
    print("\n1. INITIAL ANALYSIS")
    print("-" * 40)
    result = mind_score_api.analyze(text)
    predicted_emotion = result['emotion_analysis']['emotion']
    print(f"   Text: \"{text}\"")
    print(f"   Predicted Emotion: {predicted_emotion}")
    print(f"   Confidence: {result['emotion_analysis']['confidence']:.0%}")
    
    # Check memory system
    print("\n2. SYSTEM HEALTH BEFORE FEEDBACK")
    print("-" * 40)
    health_before = memory_system.get_system_health()
    print(f"   Overall Health: {health_before['overall_health']}")
    print(f"   Average Accuracy: {health_before['average_accuracy']:.2%}")
    print(f"   Interactions Logged: {health_before['interactions_logged']}")
    
    # Simulate feedback
    print("\n3. PROVIDING FEEDBACK")
    print("-" * 40)
    actual_emotion = "uncertain"  # Simulating ground truth
    memory_system.provide_feedback(
        interaction_index=0,
        actual_label=actual_emotion,
        feedback_type='correction'
    )
    print(f"   Feedback: Actual emotion was '{actual_emotion}'")
    print(f"   System learning: ENABLED")
    
    # Check health after feedback
    print("\n4. SYSTEM HEALTH AFTER FEEDBACK")
    print("-" * 40)
    health_after = memory_system.get_system_health()
    print(f"   Overall Health: {health_after['overall_health']}")
    print(f"   Average Accuracy: {health_after['average_accuracy']:.2%}")
    print(f"   Learning Rate: {health_after['learning_rate']:.2%}")


# =============================================================================
# EXAMPLE 9: Visualization
# =============================================================================

def example_visualization():
    """Create interactive visualizations"""
    
    text = "I love meeting people and sharing ideas! I'm creative and confident in my abilities."
    
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    result = mind_score_api.analyze(text)
    
    # Create personality DNA visualization
    traits = result['personality_analysis']['trait_scores']
    print("\n1. Creating Personality DNA Radar Chart...")
    fig = create_personality_dna_visualization(
        traits,
        title="Personality DNA Profile"
    )
    fig.show()
    print("   ✅ Personality visualization created!")
    
    print("\n2. Creating Emotion Distribution Chart...")
    # You can add additional visualizations here
    
    print("\n3. Creating Mind Score Breakdown...")
    # Additional visualizations


# =============================================================================
# EXAMPLE 10: Use Case - Customer Support Analysis
# =============================================================================

def example_customer_support():
    """Real-world use case: Analyze customer service interactions"""
    
    customer_messages = [
        "This product is amazing! Best purchase ever!",
        "I'm having issues with the defective product",
        "The customer service was terrible!",
        "Everything works perfectly, very satisfied",
        "I'm uncertain if this is the right choice"
    ]
    
    print("\n" + "="*80)
    print("CUSTOMER SUPPORT ANALYSIS")
    print("="*80)
    
    high_priority = []
    satisfied = []
    uncertain = []
    
    for message in customer_messages:
        result = mind_score_api.analyze(message, detailed=False)
        
        emotion = result['emotion_analysis']['emotion']
        mind_score = result['mind_score']['overall_score']
        danger = result['danger_detection']['danger_score']
        
        print(f"\nCustomer: \"{message}\"")
        print(f"   Emotion: {emotion}")
        print(f"   Mind Score: {mind_score:.1f}/100")
        print(f"   Satisfaction: {'High' if emotion == 'happy' else 'Low' if emotion == 'angry' else 'Moderate'}")
        
        if danger > 0.5 or emotion == 'angry':
            high_priority.append((message, mind_score))
        elif emotion == 'happy':
            satisfied.append(message)
        else:
            uncertain.append(message)
    
    # Summary
    print("\n\nSUMMARY:")
    print(f"   Satisfied Customers: {len(satisfied)}")
    print(f"   Uncertain: {len(uncertain)}")
    print(f"   High Priority/Angry: {len(high_priority)}")
    
    if high_priority:
        print("\n   HIGH PRIORITY CASES:")
        for msg, score in high_priority:
            print(f"      - {msg[:50]}... (Score: {score:.1f})")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """Run all examples (execute in notebook after initialization)"""
    
    print("\n" + "="*80)
    print("🧠 MIND READER AI SYSTEM - EXAMPLE USAGE SCRIPTS")
    print("="*80)
    
    # Uncomment the example you want to run:
    
    # example_basic_analysis()
    # example_detailed_analysis()
    # example_batch_processing()
    # example_lie_detection()
    # example_danger_detection()
    # example_personality_profiling()
    # example_conversation_analysis()
    # example_adaptive_learning()
    # example_visualization()
    # example_customer_support()
    
    print("\n" + "="*80)
    print("✅ EXAMPLES COMPLETED")
    print("="*80)
    print("\nTo run an example, uncomment the corresponding function call above")
    print("or call the function directly in a notebook cell.")
