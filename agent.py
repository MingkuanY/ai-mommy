import time
from datetime import datetime, timedelta
import pyautogui
import os
from langchain.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from typing import Optional, Literal, List, Dict
from enum import Enum
import platform
import subprocess
import json
from collections import deque

class ActionType(str, Enum):
    CONTROL = "CONTROL"
    MUSIC = "MUSIC"
    NOTIFICATION = "NOTIFICATION"
    BRIGHTNESS = "BRIGHTNESS"
    COLOR = "COLOR"

class MusicGenre(str, Enum):
    LOFI = "lofi"
    JAZZ = "jazz"
    POP = "pop"

class MonitorAction(BaseModel):
    """Single monitoring action"""
    action_type: ActionType = Field(description="The type of action to take")
    value: Optional[str] = Field(None, description="The value for the action")
    reasoning: str = Field(description="Explanation for why this action was chosen")

class MonitorResponse(BaseModel):
    """Complete monitoring response with multiple possible actions"""
    actions: List[MonitorAction] = Field(description="List of actions to take")
    analysis: str = Field(description="Overall analysis of the situation")

class UserState(BaseModel):
    """Track user's current state and activity"""
    activity: str
    stress_level: float
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # in minutes

class StateHistory:
    """Manage user state history"""
    def __init__(self, max_states=100):
        self.states: List[UserState] = []
        self.max_states = max_states
        self.current_state: Optional[UserState] = None
    
    def update_state(self, activity: str, stress_level: float):
        current_time = datetime.now()
        
        # If activity changed, close current state and start new one
        if not self.current_state or self.current_state.activity != activity:
            if self.current_state:
                self.current_state.end_time = current_time
                self.current_state.duration = int((self.current_state.end_time - self.current_state.start_time).total_seconds() / 60)
                self.states.append(self.current_state)
                
                # Maintain maximum size
                if len(self.states) > self.max_states:
                    self.states.pop(0)
            
            self.current_state = UserState(
                activity=activity,
                stress_level=stress_level,
                start_time=current_time
            )
        else:
            # Update stress level of current state
            self.current_state.stress_level = stress_level
    
    def get_recent_activities(self, minutes: int = 60) -> List[Dict]:
        """Get activities from last n minutes"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=minutes)
        
        recent_states = [
            state for state in self.states 
            if state.start_time >= cutoff_time
        ]
        
        if self.current_state:
            recent_states.append(self.current_state)
        
        return [
            {
                "activity": state.activity,
                "stress_level": state.stress_level,
                "duration": state.duration if state.duration else int((current_time - state.start_time).total_seconds() / 60),
                "start_time": state.start_time.strftime("%H:%M")
            }
            for state in recent_states
        ]

class ActionHistory:
    """Track history of actions taken"""
    def __init__(self, max_size=50):
        self.actions: deque = deque(maxlen=max_size)
    
    def add_action(self, action: MonitorAction):
        self.actions.append({
            "time": datetime.now().strftime("%H:%M"),
            "action_type": action.action_type,
            "value": action.value,
            "reasoning": action.reasoning
        })
    
    def get_recent_actions(self, count: int = 5) -> List[Dict]:
        return list(self.actions)[-count:]

class StressMonitorAgent:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        self.parser = PydanticOutputParser(pydantic_object=MonitorResponse)
        self.state_history = StateHistory()
        self.action_history = ActionHistory()
        
        self.monitor_prompt = """
        You are a helpful monitoring assistant. Based on the following information:
        
        Current Time: {time}
        Current Stress Level: {stress_level}
        Current Activity: {current_activity}
        
        Recent Activity History (last hour):
        {recent_activities}
        
        Recent Actions Taken:
        {recent_actions}
        
        Determine what interventions are needed. Consider:
        1. The time of day and appropriate activities
        2. The stress level and potential need for breaks
        3. The current activity and its appropriateness
        4. The history of recent activities and actions taken
        
        {format_instructions}
        
        Available Actions:
        - CONTROL: Use for computer control actions (e.g., closing tabs, switching applications)
        - MUSIC: Choose from genres [lofi, jazz, pop]
        - NOTIFICATION: Send user messages
        - BRIGHTNESS: Set screen brightness (1-100)
        - COLOR: Set screen color temperature in Kelvin
        
        You can recommend multiple actions if needed. For example:
        {{
            "actions": [
                {{"action_type": "NOTIFICATION", "value": "Time for a break", "reasoning": "Been working for 2 hours"}},
                {{"action_type": "MUSIC", "value": "lofi", "reasoning": "Help wind down"}}
            ],
            "analysis": "User has been working intensely and needs a break"
        }}
        
        Respond with the appropriate action(s):
        """
        
    def get_screenshot(self):
        """Take a screenshot and save it temporarily"""
        screenshot = pyautogui.screenshot()
        screenshot.save("temp_screenshot.png")
        return "temp_screenshot.png"
    
    def get_stress_level(self):
        """Read stress level from stress.txt"""
        try:
            with open("stress.txt", "r") as f:
                return float(f.read().strip())
        except:
            return 0.0
    
    def get_current_activity(self, screenshot_path):
        """Analyze current activity using active window"""
        if platform.system() == "Darwin":  # macOS
            cmd = """osascript -e 'tell application "System Events"' -e 'set frontApp to name of first application process whose frontmost is true' -e 'end tell'"""
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            return output
        elif platform.system() == "Windows":
            import win32gui
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        return "Unknown Application"
    
    def execute_action(self, action: MonitorAction):
        """Execute the recommended action"""
        print(f"Executing action: {action.action_type} with value: {action.value}")
        print(f"Reasoning: {action.reasoning}")
        
        if action.action_type == ActionType.CONTROL:
            self.execute_control(action.value)
        elif action.action_type == ActionType.MUSIC:
            self.execute_music(action.value)
        elif action.action_type == ActionType.NOTIFICATION:
            self.send_notification(action.value)
        elif action.action_type == ActionType.BRIGHTNESS:
            self.set_brightness(action.value)
        elif action.action_type == ActionType.COLOR:
            self.set_color_temperature(action.value)
        
        # Record the action in history
        self.action_history.add_action(action)
    
    def execute_control(self, command: str):
        """Execute computer control command"""
        # Add implementation using browser-use library
        print(f"Control command: {command}")
    
    def execute_music(self, genre: str):
        """Execute music genre change"""
        # Add Spotify API implementation
        print(f"Changing music to: {genre}")
    
    def send_notification(self, message: str):
        """Send system notification"""
        if platform.system() == "Darwin":  # macOS
            os.system(f"""osascript -e 'display notification "{message}" with title "Stress Monitor"'""")
        # Add Windows notification implementation
    
    def set_brightness(self, level: str):
        """Set screen brightness"""
        # Add OS-specific brightness control
        print(f"Setting brightness to: {level}")
    
    def set_color_temperature(self, temperature: str):
        """Set screen color temperature"""
        # Add OS-specific color temperature control
        print(f"Setting color temperature to: {temperature}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                # Gather current state
                current_time = datetime.now().strftime("%H:%M")
                screenshot_path = self.get_screenshot()
                stress_level = self.get_stress_level()
                current_activity = self.get_current_activity(screenshot_path)
                
                # Update state history
                self.state_history.update_state(current_activity, stress_level)
                
                # Format the prompt with current state and histories
                formatted_prompt = self.monitor_prompt.format(
                    time=current_time,
                    stress_level=stress_level,
                    current_activity=current_activity,
                    recent_activities=json.dumps(self.state_history.get_recent_activities(), indent=2),
                    recent_actions=json.dumps(self.action_history.get_recent_actions(), indent=2),
                    format_instructions=self.parser.get_format_instructions()
                )
                
                # Get AI recommendation with structured output
                response = self.llm.predict(formatted_prompt)
                monitor_response = self.parser.parse(response)
                
                # Execute all recommended actions
                print(f"Analysis: {monitor_response.analysis}")
                for action in monitor_response.actions:
                    self.execute_action(action)
                
                # Cleanup
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                
                # Wait for next check
                time.sleep(3)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(3)

def main():
    # Initialize the agent
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    agent = StressMonitorAgent(openai_api_key)
    
    # Start monitoring
    print("Starting stress monitoring...")
    agent.monitor_loop()

if __name__ == "__main__":
    main()