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
            self.logger.info("[Supabase] Updating results in Supabase. Results length: %d", len(self.results))
            response = self.supabase.table("research_history").update({
                "results": self.results
            }).eq("id", self.research_id).execute()
            self.logger.info("[Supabase] Supabase update response: %s", response)
            if hasattr(response, 'error') and response.error:
                self.logger.error("[Supabase] Supabase update failed: %s", response.error)
        except Exception as e:
            self.logger.error("[Supabase] Failed to update results in Supabase: %s", str(e))
            self.logger.error("[Supabase] Research ID: %s", self.research_id)
            self.logger.error("[Supabase] Results length: %d", len(self.results))

    def _on_message(self, ws, message):
        self.logger.info("[WebSocket] Received message: %s", message)
        if "📝 Report written for" in message:
            self.logger.info("[WebSocket] Report completion message received!")
        try:
            msg = json.loads(message)
        except Exception:
            msg = message
        if isinstance(msg, dict) and msg.get("type") == "report":
            output = msg.get("output", "")
            self.logger.info("[WebSocket] Appending report chunk. Current results length: %d", len(self.results))
            self.results += output
            self.logger.info("[WebSocket] New results length: %d", len(self.results))
            self._update_results()
        elif isinstance(msg, dict):
            self.metadata.append(msg)
            self._update_metadata()
        self.logger.info("[WebSocket] Message handling complete.")

    def _on_error(self, ws, error):
        self.logger.error("[WebSocket] Error: %s", error)
        ws.close()
        self._ws_closed = True

    def _on_close(self, ws, close_status_code, close_msg):
        self.logger.info("[WebSocket] Connection closed. Final results length: %d", len(self.results))
        self.logger.info("[WebSocket] Close status code: %s, message: %s", close_status_code, close_msg)
        self._update_results()
        self.logger.info("[WebSocket] on_close handler complete.")
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
        self._ws_thread.join(timeout=300)
        if self._ws_thread.is_alive():
            self.logger.warning("[run_task] WebSocket thread did not finish in 60s, attempting to close")
            if self._ws:
                try:
                    self._ws.close()
                except Exception as e:
                    self.logger.error("[run_task] Error closing WebSocket: %s", e)
            self._ws_thread.join(timeout=5)
        self.logger.info("[run_task] Finished research task for research_id=%s, final results length: %d", self.research_id, len(self.results))
        return {
            "research_id": self.research_id,
            "metadata": self.metadata,
            "results": self.results
        } 