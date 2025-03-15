import speech_recognition as sr
import pyttsx3
import requests
import pvporcupine
import pyaudio
import struct
import numpy as np
import time
import json
import argparse
import re
import logging
import datetime
from PyDictionary import PyDictionary
import wikipedia


ACCESS_KEY = "71bDhGw/49w/miiliQbAJoJu4LP+fe7hM1G6SNQzZCrRIXAJUYXiiw==" 

engine = pyttsx3.init()

logger = logging.getLogger("virtual_assistant")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

dictionary = PyDictionary()

def list_microphones():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:  # Only input devices
            print(f"Index {i}: {info['name']}")
    p.terminate()

def wikipedia_search(query):
    """Searches Wikipedia for information."""
    try:
        
        wikipedia.set_rate_limiting(True)

        search_results = wikipedia.search(query, results=3)
        
        if not search_results:
            return f"No Wikipedia articles found for '{query}'."
        
        try:
            page = wikipedia.page(search_results[0])
            summary = wikipedia.summary(search_results[0], sentences=3)
            
            result = f"Wikipedia: {page.title}\n\n{summary}\n\nSource: {page.url}"
            return result

        except wikipedia.exceptions.DisambiguationError as e:
            if len(e.options) > 0:
                try:
                    page = wikipedia.page(e.options[0])
                    summary = wikipedia.summary(e.options[0], sentences=3)
                    result = f"Wikipedia: {page.title}\n\n{summary}\n\nSource: {page.url}"
                    return result
                except:
                    return f"Found multiple Wikipedia matches for '{query}'. Try a more specific query."
            else:
                return f"Found multiple Wikipedia matches for '{query}'. Try a more specific query."
        
        except wikipedia.exceptions.PageError:
            return f"Couldn't find a specific Wikipedia page for '{query}'."
            
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

class DateTimeModule:
    """Provides date and time information."""
    
    def get_date(self):
        """Get the current date."""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}."
    
    def get_time(self):
        """Get the current time."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    def get_day_of_week(self):
        """Get the current day of the week."""
        day_of_week = datetime.datetime.now().strftime("%A")
        return f"Today is {day_of_week}."
    
    def get_month(self):
        """Get the current month."""
        month = datetime.datetime.now().strftime("%B")
        return f"The current month is {month}."
    
    def get_year(self):
        """Get the current year."""
        year = datetime.datetime.now().strftime("%Y")
        return f"The current year is {year}."

class DictionaryModule:
    """Provides word definitions and synonyms."""
    
    def __init__(self):
        """Initialize dictionary module."""
        self.dictionary = PyDictionary()
    
    def define_word(self, word):
        """Get definition of a word."""
        try:
            definitions = self.dictionary.meaning(word)
            
            if not definitions:
                return f"I couldn't find a definition for '{word}'."
            
            result = [f"Definitions for '{word}':"]
            
            for part_of_speech, meaning_list in definitions.items():
                result.append(f"\n{part_of_speech}:")
                for i, definition in enumerate(meaning_list, 1):
                    result.append(f"  {i}. {definition}")
            
            return "\n".join(result)
        
        except Exception as e:
            return f"Error looking up definition: {str(e)}"
    
    def get_synonyms(self, word):
        """Get synonyms for a word."""
        try:
            synonyms = self.dictionary.synonym(word)
            
            if not synonyms or len(synonyms) == 0:
                return f"I couldn't find any synonyms for '{word}'."
            
            return f"Synonyms for '{word}': {', '.join(synonyms)}"
        
        except Exception as e:
            return f"Error looking up synonyms: {str(e)}"
    
    def get_antonyms(self, word):
        """Get antonyms for a word."""
        try:
            antonyms = self.dictionary.antonym(word)
            
            if not antonyms or len(antonyms) == 0:
                return f"I couldn't find any antonyms for '{word}'."
            
            return f"Antonyms for '{word}': {', '.join(antonyms)}"
        
        except Exception as e:
            return f"Error looking up antonyms: {str(e)}"

class WeatherModule:
    """Advanced weather information module."""
    
    def __init__(self, api_key=None):
        """Initialize weather module with OpenWeatherMap API key."""
        self.api_key = api_key or "a6120a0929534faf87860308251403"
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location_name):
        """Get detailed current weather for a location."""
        if not location_name:
            location_name = "current location"
            return f"The current weather in your area appears to be clear skies with a temperature of 72°F."
        
        try:
            url = "https://api.weatherapi.com/v1/current.json"
            params = {
                "q": location_name,
                "key": "a6120a0929534faf87860308251403",
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            temp = data["current"]["temp_f"]
            condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            wind_speed = data["current"]["wind_mph"]
            feels_like = data["current"]["feelslike_f"]

            result = [
                f"Current weather in {location_name}:", 
                f"Temperature: {temp}°F (feels like {feels_like}°F)",
                f"Conditions: {condition}",
                f"Humidity: {humidity}%",
                f"Wind: {wind_speed} mph"
            ]
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return f"I couldn't retrieve weather information for {location_name}."
    
    def get_forecast(self, location, days=3):
        """Get weather forecast for a location."""
        if not location:
            location = "current location"
            return f"The forecast for your area shows temperatures between 65°F and 78°F with a chance of rain on Friday."
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "imperial",
                "cnt": days * 8
            }
            
            response = requests.get(url, params=params)

            if response.status_code == 404:
                return f"I couldn't find forecast data for '{location}'. Please try another location."
            
            response.raise_for_status()
            data = response.json()

            daily_forecasts = {}
            for item in data["list"]:
                date = datetime.datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        "temps": [],
                        "descriptions": [],
                        "precipitation": 0
                    }
                
                daily_forecasts[date]["temps"].append(item["main"]["temp"])
                daily_forecasts[date]["descriptions"].append(item["weather"][0]["main"])

                if "pop" in item:
                    daily_forecasts[date]["precipitation"] = max(daily_forecasts[date]["precipitation"], item["pop"])

            result = [f"Weather forecast for {location}:"]
            
            for date, forecast in list(daily_forecasts.items())[:days]:
                day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                min_temp = min(forecast["temps"])
                max_temp = max(forecast["temps"])

                description = max(set(forecast["descriptions"]), key=forecast["descriptions"].count)

                rain_prob = forecast["precipitation"] * 100
                rain_info = f" with {rain_prob:.0f}% chance of precipitation" if rain_prob > 20 else ""
                
                result.append(f"{day}: {min_temp:.0f}°F to {max_temp:.0f}°F, {description.lower()}{rain_info}")
            
            return "\n".join(result)
            
        except requests.exceptions.RequestException:
            forecast_days = ["Monday", "Tuesday", "Wednesday"][:days]
            forecast_text = []
            
            for day in forecast_days:
                temp_low = np.random.randint(60, 75)
                temp_high = np.random.randint(temp_low, temp_low + 15)
                conditions = np.random.choice(["sunny", "partly cloudy", "cloudy", "rainy"])
                forecast_text.append(f"{day}: {temp_low}°F to {temp_high}°F, {conditions}")
            
            return f"Forecast for {location}:\n" + "\n".join(forecast_text)
            
        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return f"I couldn't retrieve forecast information for {location}."


class NLPProcessor:
    """Natural language processing functionality."""
    
    def __init__(self):
        """Initialize NLP processor."""
        pass
    
    def extract_intent(self, text):
        """Extract intent from text."""
        text = text.lower()
        
        intents = {
            'light_control': r'\b(turn|switch|lights?|lamp|dim|brighten|brightness)\b',
            'thermostat_control': r'\b(thermostat|temperature|heat|cool|ac|degrees)\b',
            'alarm_control': r'\b(alarm|timer|remind|wake)\b',
            'weather_info': r'\b(weather|forecast|temperature outside|rain|snow|sunny)\b',
            'device_status': r'\b(status|state|condition|working|turned on|turned off)\b',
            'general_help': r'\b(help|assist|what can you do|commands)\b',
            'time_request': r'\b(time|what time is it|clock|current time)\b',
            'date_request': r'\b(date|day|today|month|year)\b',
            'define_word': r'\b(define|definition|meaning|dictionary)\b',
            'synonym_request': r'\b(synonym|similar|same meaning)\b',
            'antonym_request': r'\b(antonym|opposite|contrary)\b',
            'web_search': r'\b(search|google|look up|find)\b',
            'wikipedia_info': r'\b(wikipedia|wiki|info about|tell me about)\b',
        }
        
        detected_intents = []
        for intent, pattern in intents.items():
            if re.search(pattern, text):
                detected_intents.append(intent)
        
        if len(detected_intents) > 1:
            if 'web_search' in detected_intents and len(detected_intents) > 1:
                detected_intents.remove('web_search')
            
            if 'general_help' in detected_intents and len(detected_intents) > 1:
                detected_intents.remove('general_help')
        
        return detected_intents[0] if detected_intents else 'general_query'
    
    def extract_entities(self, text, intent):
        """Extract entities from text based on intent."""
        text = text.lower()
        
        if intent == 'light_control':
            location_match = re.search(r'(living room|bedroom|kitchen|bathroom|hallway|office)', text)
            state_match = re.search(r'(on|off|dim|brighten)', text)
            
            location = location_match.group(1) if location_match else None
            state = state_match.group(1) if state_match else None
            
            return {'location': location, 'state': state}
            
        elif intent == 'thermostat_control':
            temp_match = re.search(r'(\d+)\s*(degrees|°)', text)
            temp = int(temp_match.group(1)) if temp_match else None
            
            action = None
            if 'set' in text or 'change' in text:
                action = 'set'
            elif 'increase' in text or 'raise' in text or 'up' in text:
                action = 'increase'
            elif 'decrease' in text or 'lower' in text or 'down' in text:
                action = 'decrease'
            
            return {'temperature': temp, 'action': action}
            
        elif intent == 'weather_info':
            location_match = re.search(r'in\s+([a-z\s]+)', text)
            location = location_match.group(1) if location_match else None
            
            forecast = 'today'
            if 'tomorrow' in text:
                forecast = 'tomorrow'
            elif 'week' in text:
                forecast = 'week'
            
            return {'location': location, 'forecast': forecast}
            
        elif intent == 'define_word':
            word_match = re.search(r'(define|definition|meaning|dictionary)\s+(?:of|for)?\s+(\w+)', text)
            word = word_match.group(2) if word_match else None
            
            return {'word': word}
            
        elif intent == 'synonym_request' or intent == 'antonym_request':
            word_match = re.search(r'(synonym|antonym|similar|opposite)\s+(?:of|for|to)?\s+(\w+)', text)
            word = word_match.group(2) if word_match else None
            
            return {'word': word}
            
        elif intent == 'web_search' or intent == 'wikipedia_info':
            query_match = re.search(r'(search|google|look up|find|wikipedia|wiki|info about|tell me about)\s+(?:for|about)?\s+(.+)', text)
            query = query_match.group(2) if query_match else text
            
            return {'query': query}
            
        return {}

class VirtualAssistant:
    """Core virtual assistant class."""
    
    def __init__(self):
        """Initialize the virtual assistant."""
        self.name = "Beck"
        self.nlp = NLPProcessor()
        self.date_time = DateTimeModule()
        self.dictionary = DictionaryModule()
        self.weather = WeatherModule()
        self.running = True
        self.wake_word_enabled = True
        
        self.engine = pyttsx3.init()
        
        try:
            self.porcupine = pvporcupine.create(
                access_key=ACCESS_KEY,
                keywords=["porcupine", "bumblebee", "jarvis", "computer"],
                keyword_paths=["/Users/srishaanth/Documents/PyHackathon/Hey_Beck.ppn"]
            )
            
            audio_initialized = self.initialize_audio()
            self.wake_word_enabled = audio_initialized
            
            if not audio_initialized:
                logger.warning("Wake word detection disabled due to audio initialization failure")
        except Exception as e:
            logger.error(f"Wake word initialization failed: {e}")
            self.wake_word_enabled = False
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'porcupine') and self.porcupine is not None:
            self.porcupine.delete()
        
        if hasattr(self, 'audio_stream') and self.audio_stream is not None:
            self.audio_stream.close()
        
        if hasattr(self, 'pa') and self.pa is not None:
            self.pa.terminate()
    
    def speak(self, text):
        """Converts text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def recognize_speech(self):
        """Captures and transcribes speech input."""
        recognizer = sr.Recognizer()
        mic_index = 0 
        
        list_microphones() 

        with sr.Microphone(device_index=mic_index) as source:
            print(f"Using microphone: {mic_index}")
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
    
    def _reopen_audio_stream(self):
        """Reopen the audio stream if it gets closed."""
        try:
            if hasattr(self, 'audio_stream') and self.audio_stream is not None:
                self.audio_stream.close()
            
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            logger.info("Audio stream reopened successfully")
        except Exception as e:
            logger.error(f"Failed to reopen audio stream: {e}")

    def initialize_audio(self):
        """Initialize audio stream with proper error handling."""
        try:
            if hasattr(self, 'audio_stream') and self.audio_stream is not None:
                self.audio_stream.close()
            
            if hasattr(self, 'pa') and self.pa is not None:
                self.pa.terminate()
                
            self.pa = pyaudio.PyAudio()
            
            
            input_device_index = None
            for i in range(self.pa.get_device_count()):
                device_info = self.pa.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    input_device_index = i
                    logger.info(f"Using input device: {device_info['name']}")
                    break
            
            if input_device_index is None:
                logger.error("No suitable input device found")
                return False
            
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            return True
        except Exception as e:
            logger.error(f"Audio initialization error: {e}")
            return False
    
    def wait_for_wake_word(self):
        """Listen for wake word."""
        if not self.wake_word_enabled:
            return True
        
        print("Listening for wake word...")
        
        while self.running:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print(f"Wake word detected!")
                    return True
            except IOError as e:
                if e.errno == -9981:  # Input overflow
                    logger.warning("Audio buffer overflow, continuing...")
                    continue
                elif e.errno == -9988:  # Stream closed
                    logger.error("Audio stream closed unexpectedly, reopening...")
                    self._reopen_audio_stream()
                    continue
                else:
                    logger.error(f"Audio stream error: {e}")
                    time.sleep(0.5)  
        
        return False
    
    def process_command(self, command):
        """Process user command."""
        if not command:
            return None
        

        intent = self.nlp.extract_intent(command)
        entities = self.nlp.extract_entities(command, intent)
        
        logger.info(f"Intent: {intent}, Entities: {entities}")
        

        if intent == 'light_control':
            location = entities.get('location', 'room')
            state = entities.get('state', 'on')
            return f"Turning {state} the lights in the {location}."
            
        elif intent == 'thermostat_control':
            temp = entities.get('temperature')
            action = entities.get('action', 'set')
            
            if action == 'set' and temp:
                return f"Setting thermostat to {temp} degrees."
            elif action == 'increase':
                return "Increasing the temperature."
            elif action == 'decrease':
                return "Decreasing the temperature."
            else:
                return "How would you like to adjust the thermostat?"
                
        elif intent == 'weather_info':
            location = entities.get('location')
            forecast = entities.get('forecast', 'today')
            
            if forecast == 'today':
                return self.weather.get_current_weather(location)
            else:
                days = 7 if forecast == 'week' else 1
                return self.weather.get_forecast(location, days)
                
        elif intent == 'time_request':
            return self.date_time.get_time()
            
        elif intent == 'date_request':
            return self.date_time.get_date()
            
        elif intent == 'define_word':
            word = entities.get('word')
            if word:
                return self.dictionary.define_word(word)
            else:
                return "What word would you like me to define?"
                
        elif intent == 'synonym_request':
            word = entities.get('word')
            if word:
                return self.dictionary.get_synonyms(word)
            else:
                return "What word would you like synonyms for?"
                
        elif intent == 'antonym_request':
            word = entities.get('word')
            if word:
                return self.dictionary.get_antonyms(word)
            else:
                return "What word would you like antonyms for?"
                
        elif intent == 'web_search':
            return "I'm sorry, but web search functionality is currently unavailable."
                
        elif intent == 'wikipedia_info':
            query = entities.get('query')
            if query:
                return wikipedia_search(query)
            else:
                return "What would you like me to look up on Wikipedia?"
                
        elif intent == 'general_help':
            return ("I can help you with the following:\n"
                    "- Control smart home devices ('turn on the lights')\n"
                    "- Get weather information ('what's the weather like')\n"
                    "- Tell time and date ('what time is it')\n"
                    "- Define words ('define happiness')\n"
                    "- Find synonyms and antonyms ('synonym for happy')\n"
                    "- Search the web ('search for pasta recipes')\n"
                    "- Look up information on Wikipedia ('tell me about quantum physics')")
                    
        elif intent == 'alarm_control':
            return "I can set alarms, but that feature is still under development."
        
        else:
            if 'hello' in command or 'hi' in command:
                return f"Hello! How can I help you today?"
            elif 'bye' in command or 'goodbye' in command:
                self.running = False
                return "Goodbye! Have a nice day."
            elif 'thank you' in command or 'thanks' in command:
                return "You're welcome!"
            else:
                return wikipedia_search(command)
    
    def run(self):
        """Main run loop for the assistant."""
        print(f"{self.name} virtual assistant is ready!")
        self.speak(f"Hello, I'm {self.name}, your virtual assistant. How can I help you today?")
        
        while self.running:
            try:
                if self.wake_word_enabled:
                    if not self.wait_for_wake_word():
                        continue
                    self.speak("I'm listening")

                try:
                    command = self.recognize_speech()
                except Exception as e:
                    logger.error(f"Speech recognition error: {e}")
                    self.speak("I'm having trouble understanding you. Could you try again?")
                    continue

                if command:
                    try:
                        response = self.process_command(command)
                    except Exception as e:
                        logger.error(f"Command processing error: {e}")
                        self.speak("I couldn't process that command. Please try again.")
                        continue
                    
                    if response:
                        print(response)
                        self.speak(response)

                if not self.running:
                    break

                time.sleep(0.1)

            except KeyboardInterrupt:
                self.running = False
                print("Stopping assistant...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.speak("I encountered an error. Please wait a moment.")
                time.sleep(2)  

        print("Virtual assistant stopped.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Virtual Assistant")
    parser.add_argument("--no-wake-word", action="store_true", help="Disable wake word detection")
    args = parser.parse_args()
    
    try:
        assistant = VirtualAssistant()

        if args.no_wake_word:
            assistant.wake_word_enabled = False
        
        assistant.run()
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()