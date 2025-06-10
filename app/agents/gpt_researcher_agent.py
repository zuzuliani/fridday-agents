import websocket
import json
import threading
import uuid
from app.supabase_integration import get_supabase_client
import logging

class GPTResearcherAgent:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.supabase = None  # Will be set per request
        self.research_id = None
        self.metadata = []
        self.results = None
        self.user_id = None
        self.topic = None
        self._ws_thread = None
        self._ws = None
        self._ws_closed = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def set_supabase_client(self, jwt_token):
        self.supabase = get_supabase_client()
        self.supabase.postgrest.auth(jwt_token)

    def _insert_initial_row(self):
        self.supabase.table("research_history").insert({
            "id": self.research_id,
            "user_id": self.user_id,
            "topic": self.topic,
            "metadata": self.metadata,
            "results": self.results
        }).execute()

    def _update_metadata(self):
        self.supabase.table("research_history").update({
            "metadata": self.metadata
        }).eq("id", self.research_id).execute()

    def _update_results(self):
        try:
            print("DEBUG: Updating results in Supabase:", self.results[:100] + "..." if len(self.results) > 100 else self.results)
            response = self.supabase.table("research_history").update({
                "results": self.results
        }).eq("id", self.research_id).execute()
            print("DEBUG: Supabase update response:", response)
            if hasattr(response, 'error') and response.error:
                print("ERROR: Supabase update failed:", response.error)
        except Exception as e:
            print("ERROR: Failed to update results in Supabase:", str(e))
            print("ERROR: Research ID:", self.research_id)
            print("ERROR: Results length:", len(self.results))

    def _on_message(self, ws, message):
        self.logger.info("[WebSocket] Received message: %s", message)
        try:
            msg = json.loads(message)
        except Exception:
            msg = message
        if isinstance(msg, dict) and msg.get("type") == "report":
            output = msg.get("output", "")
            print("DEBUG: Appending report chunk:", output)
            print("DEBUG: Current results length:", len(self.results))
            self.results += output
            print("DEBUG: New results length:", len(self.results))
            self._update_results()
        elif isinstance(msg, dict):
            self.metadata.append(msg)
            self._update_metadata()
        print("Received:", message)

    def _on_error(self, ws, error):
        self.logger.error("[WebSocket] Error: %s", error)
        ws.close()
        self._ws_closed = True

    def _on_close(self, ws, close_status_code, close_msg):
        self.logger.info("[WebSocket] Connection closed")
        self._update_results()
        self._ws_closed = True

    def _on_open(self, ws, payload):
        self.logger.info("[WebSocket] Opened connection, sending payload")
        ws.send(payload)

    def run_task(self, task, report_type, report_source, tone, user_id, topic, jwt_token, headers=None):
        self.logger.info("[run_task] Starting research task for user_id=%s, topic=%s", user_id, topic)
        self.set_supabase_client(jwt_token)
        self.user_id = user_id
        self.topic = topic
        self.research_id = str(uuid.uuid4())
        self.metadata = []
        self.results = ""
        self._insert_initial_row()
        
        payload_data = {
            "task": task,
            "report_type": report_type,
            "report_source": report_source,
            "tone": tone
        }
        
        if headers:
            payload_data["headers"] = headers
            
        payload = f'start {json.dumps(payload_data)}'
        
        self._ws_closed = False
        self._ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=lambda ws: self._on_open(ws, payload),
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self._ws_thread = threading.Thread(target=self._ws.run_forever)
        self.logger.info("[run_task] Starting WebSocket thread")
        self._ws_thread.start()
        self._ws_thread.join(timeout=60)
        if self._ws_thread.is_alive():
            self.logger.warning("[run_task] WebSocket thread did not finish in 60s, attempting to close")
            if self._ws:
                try:
                    self._ws.close()
                except Exception as e:
                    self.logger.error("[run_task] Error closing WebSocket: %s", e)
            self._ws_thread.join(timeout=5)
        self.logger.info("[run_task] Finished research task for research_id=%s", self.research_id)
        return {
            "research_id": self.research_id,
            "metadata": self.metadata,
            "results": self.results
        } 