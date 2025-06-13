import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import datetime
import requests
import base64
import re

load_dotenv()

translation_languages = {
    '1': ('English', 'en-IN'),
    '2': ('Hindi', 'hi-IN'),
    '3': ('Tamil', 'ta-IN'),
    '4': ('Telugu', 'te-IN'),
    '5': ('Kannada', 'kn-IN'),
    '6': ('Malayalam', 'ml-IN'),
    '7': ('Marathi', 'mr-IN'),
    '8': ('Gujarati', 'gu-IN'),
    '9': ('Punjabi', 'pa-IN'),
    '10': ('Bengali', 'bn-IN'),
    '11': ('Odia', 'od-IN')
}

def display_language_menu():
    """Display available language options."""
    print("\nAvailable Languages:")
    print("-" * 35)
    for key, (name, code) in translation_languages.items():
        print(f"{key:2}. {name} ({code})")
    print("-" * 35)

def display_output_menu():
    """Display output format options."""
    print("\n📋 Choose Output Format:")
    print("-" * 25)
    print("1. Text-to-Text (Display translated text)")
    print("2. Text-to-Speech (Play translated audio)")
    print("-" * 25)

def translate_text(text: str, target_lang: str) -> str:
    """
    Function to translate text using Sarvam AI's translation API.
    """
    url = "https://api.sarvam.ai/translate"
    
    headers = {
        "Content-Type": "application/json",
        "API-Subscription-Key": os.getenv("SARVAM_API_KEY")
    }
    
    payload = {
        "input": text,
        "source_language_code": "auto",
        "target_language_code": target_lang,
        "model": "mayura:v1"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Debug - Translation Response status: {response.status_code}")
            print(f"Debug - Translation Response text: {response.text}")
        
        response.raise_for_status()
        result = response.json()
        return result["translated_text"]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Translation failed: {e}")
        return text
    except KeyError as e:
        print(f"❌ Translation response format error: {e}")
        return text

def chunk_text_for_tts(text: str, max_chars: int = 450) -> list:
    """
    Chunk text into smaller pieces for TTS API (max 500 chars per chunk).
    Tries to break at sentence boundaries when possible.
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    # Split by sentences first
    sentences = re.split(r'[.!?]+', text)
    
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence would exceed limit, save current chunk
        if len(current_chunk) + len(sentence) + 1 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # If single sentence is too long, split by words
                words = sentence.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > max_chars:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word
                        else:
                            # If single word is too long, force split
                            chunks.append(word[:max_chars])
                            temp_chunk = word[max_chars:]
                    else:
                        temp_chunk += " " + word if temp_chunk else word
                if temp_chunk:
                    current_chunk = temp_chunk
        else:
            current_chunk += ". " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def text_to_speech_sarvam(text: str, lang: str, output_file: str = "translated_speech.wav") -> None:
    """
    Function to convert text to speech using Sarvam AI API.
    Handles text chunking for long texts (500 char limit per API call).
    """
    url = "https://api.sarvam.ai/text-to-speech"
    
    headers = {
        "Content-Type": "application/json",
        "API-Subscription-Key": os.getenv("SARVAM_API_KEY")
    }
    
    # Chunk the text if it's too long
    text_chunks = chunk_text_for_tts(text)
    print(f"🔊 Converting {len(text_chunks)} text chunk(s) to speech in {lang}...")
    
    all_audio_data = b""
    
    for i, chunk in enumerate(text_chunks):
        print(f"Processing chunk {i+1}/{len(text_chunks)}...")
        
        payload = {
            "inputs": [chunk],
            "target_language_code": lang,
            "speaker": "meera",
            "model": "bulbul:v1"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"Debug - TTS Response status: {response.status_code}")
                print(f"Debug - TTS Response text: {response.text}")
                continue
            
            response.raise_for_status()
            result = response.json()
            
            # Handle different possible response formats
            if "audios" in result:
                audio_base64 = result["audios"][0]
            elif "audio" in result:
                audio_base64 = result["audio"]
            else:
                print(f"❌ Unexpected response format: {result}")
                continue
            
            audio_data = base64.b64decode(audio_base64)
            all_audio_data += audio_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Text-to-speech failed for chunk {i+1}: {e}")
            continue
        except KeyError as e:
            print(f"❌ TTS response format error for chunk {i+1}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error processing chunk {i+1}: {e}")
            continue
    
    if all_audio_data:
        with open(output_file, "wb") as f:
            f.write(all_audio_data)
        
        print(f"✓ Audio saved as {output_file}")
        
        # Play the audio file
        if os.name == 'nt':  # Windows
            os.system(f"start {output_file}")
        elif os.name == 'posix':  # macOS/Linux
            import platform
            if platform.system() == "Darwin":  # macOS
                os.system(f"afplay {output_file}")
            else:  # Linux
                os.system(f"mpg123 {output_file} || aplay {output_file}")
    else:
        print("❌ No audio data generated")

def init_chatbot(vectorstore):
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )
    retriever = vectorstore.as_retriever()

    contextualize_q_system_prompt = (
        "Given the chat history and the latest user question about mineral predictive mapping, geological exploration, or mineral discovery topics, reformulate the question to make it standalone and clear. "
        "Do NOT answer the question, just reformulate it. "
        "If it's already clear, return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_system_prompt = (
        "You are a knowledgeable and concise mineral exploration and geological assistant. "
        "Use the provided geological and mineral exploration context to answer questions about "
        "mineral predictive mapping, geological surveys, mining exploration, and mineral discovery accurately. "
        "If you are unsure or do not know the answer, say that you don't know. "
        "Provide a concise, evidence-based response in no more than three sentences, "
        "and focus on technical accuracy while avoiding speculation without sufficient geological data."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain

def chat(rag_chain):
    chat_history = []
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit", "bye"]:
            break
        
        # Language selection
        display_language_menu()
        print("\n")
        lang_number = input("Enter the language number from the above menu: ")
        
        if lang_number not in translation_languages:
            print("❌ Invalid language choice. Please try again.")
            continue
            
        lang_code = translation_languages[lang_number][1]
        lang_name = translation_languages[lang_number][0]
        
        # Skip translation and TTS for English
        if lang_code == 'en-IN':
            print("------------" + "Answer in English" + "---------------")
            result = rag_chain.invoke({"input": query, "chat_history": chat_history}) 
            print(f"AI: {result['answer']}")
            print("\n" + "="*50 + "\n")
            
            # Update chat history
            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=result["answer"]))
            continue
        
        # Output format selection for non-English languages
        display_output_menu()
        output_choice = input("Choose output format (1 or 2): ").strip()
        
        if output_choice not in ['1', '2']:
            print("❌ Invalid output choice. Please select 1 or 2.")
            continue
        
        # Process the user's query through the retrieval chain
        print("------------" + "Answer in English" + "---------------")
        result = rag_chain.invoke({"input": query, "chat_history": chat_history}) 
        print(f"AI: {result['answer']}")
        print("\n")
        
        # Get translated text
        translated_answer = translate_text(result["answer"], lang_code)
        
        print(f"------------" + f"Answer in {lang_name}" + "---------------")
        
        if output_choice == '1':
            # Text-to-Text: Display translated text
            print(f"AI_Translated: {translated_answer}")
            
        elif output_choice == '2':
            # Text-to-Speech: Generate and play audio
            print("🔊 Generating speech audio...")
            
            # Create unique filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"chat_response_{lang_code}_{timestamp}.wav"
            
            # Convert to speech and play
            text_to_speech_sarvam(translated_answer, lang_code, output_filename)
            print(f"✓ Audio response generated in {lang_name}")
        
        print("\n" + "="*50 + "\n")
        
        # Update the chat history
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=result["answer"]))
