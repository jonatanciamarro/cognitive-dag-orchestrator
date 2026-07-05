"""Capability Registry + MCP Layer — Prevent duplicate agents, enable tool interoperability.

Registra capacidades de cada agente e ferramenta:
- O que cada agente FAZ (capabilities)
- O que cada agente PRECISA (dependencies)
- Inputs e outputs esperados
- Dono do agente

MCP Layer:
- Adaptador universal para ferramentas
- Suporte a MCP servers locais e remotos
- Descoberta automatica de ferramentas
"""

from __future__ import annotations
import time
from datetime import datetime, timezone

import json
import subprocess
import threading
from dataclasses import dataclass, field
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
# CAPABILITY REGISTRY
# ═══════════════════════════════════════════════════════════════════


@dataclass
class AgentCapability:
    """Declaracao de capacidade de um agente."""

    agent_name: str
    capability: str  # e.g. "image_generation", "seo_research"
    description: str = ""
    inputs: dict[str, str] = field(default_factory=dict)  # param -> type
    outputs: dict[str, str] = field(default_factory=dict)  # field -> type
    dependencies: list[str] = field(default_factory=list)  # agent dependencies
    owner: str = ""
    version: str = "1.0.0"
    quality_score: float = 5.0  # 1-10
    avg_duration_ms: int = 0
    success_rate: float = 1.0  # 0-1

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "capability": self.capability,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "owner": self.owner,
            "version": self.version,
            "quality_score": self.quality_score,
            "avg_duration_ms": self.avg_duration_ms,
            "success_rate": self.success_rate,
        }


class CapabilityRegistry:
    """Registry that prevents duplicate agent capabilities.

    Cada agente deve declarar suas capacidades.
    O registry detecta:
    - Capacidades duplicadas (dois agentes fazendo a mesma coisa)
    - Capacidades orfas (ninguem produz o que outro precisa)
    - Dependencias circulares
    """

    _instance: "CapabilityRegistry | None" = None
    _lock = threading.Lock()

    def __init__(self):
        self._capabilities: dict[str, AgentCapability] = {}  # agent_name -> capability
        self._capability_map: dict[
            str, list[str]
        ] = {}  # capability_type -> [agent_names]

    @staticmethod
    def get_instance() -> "CapabilityRegistry":
        if CapabilityRegistry._instance is None:
            with CapabilityRegistry._lock:
                if CapabilityRegistry._instance is None:
                    CapabilityRegistry._instance = CapabilityRegistry()
        return CapabilityRegistry._instance

    def register(self, capability: AgentCapability) -> None:
        """Register an agent's capabilities."""
        with self._lock:
            self._capabilities[capability.agent_name] = capability
            if capability.capability not in self._capability_map:
                self._capability_map[capability.capability] = []
            self._capability_map[capability.capability].append(capability.agent_name)

    def find_duplicates(self) -> list[dict[str, Any]]:
        """Find capabilities that have multiple agents."""
        duplicates = []
        for cap_type, agents in self._capability_map.items():
            if len(agents) > 1:
                duplicates.append(
                    {
                        "capability": cap_type,
                        "agents": agents,
                        "suggestion": "Review if these agents are truly distinct "
                        f"or if {agents[0]} can replace the others",
                    }
                )
        return duplicates

    def find_gaps(self) -> list[str]:
        """Find dependencies that no agent satisfies."""
        all_deps = set()
        all_caps = set(self._capability_map.keys())
        for cap in self._capabilities.values():
            all_deps.update(cap.dependencies)
        missing = all_deps - all_caps
        return sorted(missing)

    def find_cycles(self) -> list[list[str]]:
        """Detect circular dependencies between agents."""
        deps: dict[str, list[str]] = {}
        for cap in self._capabilities.values():
            deps[cap.agent_name] = cap.dependencies

        cycles = []
        visited: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            for dep in deps.get(node, []):
                if dep in deps:
                    dfs(dep)
            path.pop()

        for agent in deps:
            dfs(agent)

        # Remove duplicates
        unique_cycles = []
        seen = set()
        for cycle in cycles:
            key = tuple(sorted(cycle))
            if key not in seen:
                seen.add(key)
                unique_cycles.append(cycle)
        return unique_cycles

    def get_all_capabilities(self) -> list[dict[str, Any]]:
        """Get all registered capabilities."""
        return [c.to_dict() for c in self._capabilities.values()]

    def find_by_capability(self, capability: str) -> list[str]:
        """Find agents that provide a specific capability."""
        return self._capability_map.get(capability, [])

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the registry."""
        with self._lock:
            return {
                "total_agents": len(self._capabilities),
                "total_capabilities": len(self._capability_map),
                "duplicates": self.find_duplicates(),
                "gaps": self.find_gaps(),
                "cycles": self.find_cycles(),
            }


# ═══════════════════════════════════════════════════════════════════
# MCP TOOL ADAPTER
# ═══════════════════════════════════════════════════════════════════


@dataclass
class MCPTool:
    """A tool exposed via MCP (Model Context Protocol)."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    server: str = "local"  # "local" or "remote"
    command: str = ""  # For local servers: command to run
    url: str = ""  # For remote servers
    enabled: bool = True
    cache_ttl: int = 0  # Seconds to cache results (0 = no cache)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "server": self.server,
            "enabled": self.enabled,
        }


class MCPRegistry:
    """Registry for MCP-compatible tools.

    Suporta:
    - Ferramentas locais (executadas via subprocess)
    - Ferramentas remotas (HTTP API)
    - Cache de resultados
    - Descoberta automatica
    """

    _instance: "MCPRegistry | None" = None
    _lock = threading.Lock()

    def __init__(self):
        self._tools: dict[str, MCPTool] = {}
        self._cache: dict[str, tuple[Any, float]] = {}  # key -> (result, expiry)

    @staticmethod
    def get_instance() -> "MCPRegistry":
        if MCPRegistry._instance is None:
            with MCPRegistry._lock:
                if MCPRegistry._instance is None:
                    MCPRegistry._instance = MCPRegistry()
        return MCPRegistry._instance

    def register_tool(self, tool: MCPTool) -> None:
        """Register an MCP-compatible tool."""
        with self._lock:
            self._tools[tool.name] = tool

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name with the given arguments."""
        with self._lock:
            if tool_name not in self._tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            tool = self._tools[tool_name]

        # Check cache
        if tool.cache_ttl > 0:
            cache_key = f"{tool_name}:{json.dumps(kwargs, sort_keys=True)}"
            with self._lock:
                if cache_key in self._cache:
                    result, expiry = self._cache[cache_key]
                    if time.time() < expiry:
                        return result

        # Execute based on server type
        if tool.server == "local" and tool.command:
            result = self._run_local(tool, kwargs)
        elif tool.server == "remote" and tool.url:
            result = self._run_remote(tool, kwargs)
        else:
            raise ValueError(f"No execution method for tool '{tool_name}'")

        # Cache result if needed
        if tool.cache_ttl > 0:
            with self._lock:
                self._cache[cache_key] = (result, time.time() + tool.cache_ttl)

        return result

    def _run_local(self, tool: MCPTool, kwargs: dict) -> Any:
        """Run a local MCP tool via subprocess."""
        import shlex

        try:
            cmd = tool.command.format(**kwargs)
            result = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Tool '{tool.name}' timed out"}
        except Exception as e:
            return {"error": str(e)}

    def _run_remote(self, tool: MCPTool, kwargs: dict) -> Any:
        """Run a remote MCP tool via HTTP API."""
        import urllib.request
        import json

        try:
            data = json.dumps(kwargs).encode()
            req = urllib.request.Request(
                tool.url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [t.to_dict() for t in self._tools.values()]

    def get_tool(self, name: str) -> MCPTool | None:
        return self._tools.get(name)


__all__ = [
    "CapabilityRegistry",
    "AgentCapability",
    "MCPRegistry",
    "MCPTool",
]
