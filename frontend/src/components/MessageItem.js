import ReactMarkdown from "react-markdown";
import ToolStartCard from "./ToolStartCard";
import ToolResultCard from "./ToolResultCard";

export default function MessageItem({ msg }) {
  if (msg.type === "user") {
    return (
      <div className="msg msg-user">
        <div className="bubble bubble-user">{msg.text}</div>
      </div>
    );
  }
  if (msg.type === "tool_start") {
    return (
      <div className="msg msg-tool">
        <ToolStartCard tool={msg.tool} />
      </div>
    );
  }
  if (msg.type === "tool_result") {
    return (
      <div className="msg msg-result">
        <ToolResultCard tool={msg.tool} result={msg.result} />
      </div>
    );
  }
  if (msg.type === "assistant") {
    return (
      <div className="msg msg-assistant">
        <div className="avatar">CL</div>
        <div className="bubble bubble-assistant">
          <ReactMarkdown>{msg.text}</ReactMarkdown>
        </div>
      </div>
    );
  }
  return null;
}
