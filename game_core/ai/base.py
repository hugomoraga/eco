from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AIResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class AIAdapter(ABC):
    @abstractmethod
    def generate_npc(self, context: dict) -> AIResponse:
        pass

    @abstractmethod
    def generate_event(self, context: dict) -> AIResponse:
        pass

    @abstractmethod
    def summarize_history(self, events: list[dict]) -> AIResponse:
        pass

    @abstractmethod
    def interpret_consequences(self, situation: dict) -> AIResponse:
        pass

    @abstractmethod
    def generate_manifesto(self, essence: str, context: dict) -> AIResponse:
        pass


MANIFESTO_TEMPLATES: dict[str, str] = {
    "anarchism": """La libertad no se pide, se toma. En las calles, en los barrios, en los lugares de trabajo, los pueblos estan demostrando que no necesitamos autoridades ni Estados para organizarnos. La horizontalidad no es un ideal utopico, es una practica cotidiana cuando desaparece la coercion.

La autonomia personal crece cuando los vinculos son voluntarlos y horizontales. No hay lider que siga ni subdito que obedezca. Cada decision se toma entre iguales, con consenso, sin jerarquias. El verdadero poder reside en la accion colectiva y la solidaridad directa.

Ningun humano es ilegal. Ningun muro nos separa. Abajo el Estado y toda autoridad que no pueda justificar su existencia. Libertad para todos los pueblos que quieran gobernarse sin amos. La revolucion es hoy, es aqui, es ahora.""",

    "technocracy": """El conocimiento es la base de toda sociedad que aspire a la prosperidad. Solo mediante la ciencia y la tecnica podemos resolver los problemas que aquejan a nuestra civilizacion. Los expertos deben governar, no los demagogos ni los ideologos.

Los protocolos existen porque han demostrado funcionar. La eficiencia no es fria, es compassion aplicada con rigor. Cuando un sistema funciona bien, todos se benefician. Los errores provienen de la ignorancia, no de la racionalidad. La mejora continua es nuestro compromiso con la humanidad.

Que gane el mejor argumento. Que gobiernen los que mas saben. Ciencia y progreso para todos. No hay lugar para la supersticion cuando la evidencia esta disponible.""",

    "absurdism": """Todo es absurdo. El universo no tiene sentido, la vida no tiene proposito, y sin embargo aqui estamos, pensando en ello. La unica respuesta coherente a este sinsentido es reir. La risa es el unico acto verdaderamente racional ante lo irracional.

Carpe diem, pero con ironia. Tomamos lo que podemos, esperamos lo minimo, y reimos de todo, especialmente de nosotros mismos. El absurdo no es pesimismo, es claridad. Cuando aceptas que nada importa, todo se vuelve divertido.

Que venga el caos. Nosotros lo abrazamos. Sin sentido no hay decepcion. El vacio es libertad. La existencia precede a la esencia, asi que inventemos la nuestra.""",

    "thelema": """Tu voluntad es tu unica ley. No hay mandamientos externos que signifiquen nada. El individuo es la medida de todas las cosas. La grandeza esta dentro de ti, solo tienes que despertarla.

La magia es la voluntad en accion. El destino no esta escrito, se escribe. Cada acto de voluntad es un acto magico que modifica la realidad segun tus deseos. No hay bien ni mal, solo poder y quienes lo usan.

Tu eres Dios. Yo soy Dios. Todos somos Dioses. La unica verdad es la voluntad manifestada. Haz lo que quieras sera toda la ley. Amor es la ley, amor bajo voluntad.""",

    "ecology": """La tierra no nos pertenece, nosotros pertenecemos a la tierra. Los ecosistemas son sistemas complejos que han evolucionado durante millones de anos. Interferir con ellos tiene consecuencias que apenas empezamos a comprender.

La sostenibilidad no es una opcion, es una necesidad. El crecimiento infinito en un planeta finito es la locura mas grande de nuestra civilizacion. Volvamos a lo que funciona: ciclos cerrados, recursos renovables, respeto por todas las formas de vida.

La naturaleza sabe mejor que nosotros. Menos es mas. Cero crecimiento, maxima vida. El planeta sobrevivira a nuestra especie, pero nosotros somos responsables de cuidarlo.""",
}


class MockAdapter(AIAdapter):
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.sequential = self.config.get("sequential", True)
        self.loop = self.config.get("loop", True)
        self._npc_index = 0
        self._event_index = 0
        self._history_index = 0

    def generate_npc(self, context: dict) -> AIResponse:
        from game_core.i18n import t

        npc_keys = ["dra_maela_ruun", "karax_el_sin_amo", "hermano_vacio"]
        idx = self._npc_index
        if self.sequential:
            self._npc_index = (self._npc_index + 1) % len(npc_keys)
            if not self.loop and self._npc_index == 0:
                self._npc_index = len(npc_keys) - 1

        key = npc_keys[idx]
        npc_data = t(f"npcs:{key}")

        return AIResponse(success=True, data=npc_data)

    def generate_event(self, context: dict) -> AIResponse:
        from game_core.i18n import t

        event_keys = ["la_huelga_del_silencio", "el_laboratorio_abierto"]
        idx = self._event_index
        if self.sequential:
            self._event_index = (self._event_index + 1) % len(event_keys)
            if not self.loop and self._event_index == 0:
                self._event_index = len(event_keys) - 1

        key = event_keys[idx]
        event_data = t(f"events:{key}")

        return AIResponse(success=True, data=event_data)

    def summarize_history(self, events: list[dict]) -> AIResponse:
        summaries = [
            "Ano 47: La idea de la Voluntad Colectiva Calculada comenzo a gestarse.",
            "Ano 52: Los Protocolos Autonomos se expandieron a tres distritos.",
            "Ano 61: Una faccion se radicalizo hacia el absurdo.",
        ]

        idx = self._history_index
        if self.sequential:
            self._history_index = (self._history_index + 1) % len(summaries)
            if not self.loop and self._history_index == 0:
                self._history_index = len(summaries) - 1

        return AIResponse(success=True, data={"summary": summaries[idx]})

    def interpret_consequences(self, situation: dict) -> AIResponse:
        return AIResponse(
            success=True,
            data={
                "interpretation": "La faccion muestra signos de deriva ideologica.",
                "recommendations": ["Monitorear", "Intervenir", "Ignorar"],
            },
        )

    def generate_manifesto(self, essence: str, context: dict) -> AIResponse:
        manifesto = MANIFESTO_TEMPLATES.get(essence, MANIFESTO_TEMPLATES["anarchism"])
        return AIResponse(success=True, data={"content": manifesto, "essence": essence})
