from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class NarrativeAction:
    verb: str
    text: str
    location: str


NARRATIVE_ACTIONS: dict[str, list[dict]] = {
    "conversar": [
        {"verb": "conversó", "text": "con los vecinos sobre el cambio", "location": "en el mercado"},
        {"verb": "tuvo", "text": "una reunión secreta en el sótano", "location": "de la taberna"},
        {"verb": "intercambió", "text": "ideas con comerciantes locales", "location": "en el bazar"},
        {"verb": "habló", "text": "con artesanos sobre la situación", "location": "en el taller"},
        {"verb": "conversó", "text": "con estudiantes en la biblioteca", "location": "del barrio"},
        {"verb": "discutió", "text": "planes con un grupo reducido", "location": "en la azotea"},
        {"verb": "conversó", "text": "con trabajadores en el muelle", "location": "del puerto"},
        {"verb": "tuvo", "text": "una tertulia nocturna", "location": "en la casa de un simpatizante"},
    ],
    "propagar": [
        {"verb": "distribuyó", "text": "panfletos revolucionarios", "location": "en el mercado"},
        {"verb": "colgó", "text": "pancartas en la plaza central", "location": "de la ciudad"},
        {"verb": "esparció", "text": "ideas en el distrito norte", "location": "de la ciudad"},
        {"verb": "difundió", "text": "mensajes en los muros del barrio", "location": "industrial"},
        {"verb": "propagó", "text": "su mensaje entre los comerciantes", "location": "del mercado"},
        {"verb": "repartió", "text": "volantes en la entrada de la fábrica", "location": ""},
        {"verb": "publicó", "text": "escritos en tablones públicos", "location": "de la calle principal"},
        {"verb": "difundió", "text": "las ideas del Echo", "location": "en el teatro abandonado"},
    ],
    "predicar": [
        {"verb": "predicó", "text": "ante una multitud congregada", "location": "en la plaza"},
        {"verb": "dio", "text": "un sermón sobre la libertad", "location": "en la catedral"},
        {"verb": "arengó", "text": "a los trabajadores del puerto", "location": ""},
        {"verb": "predicó", "text": "sobre el cambio necesario", "location": "en la taberna"},
        {"verb": "proclamó", "text": "ideas revolucionarias", "location": "desde el balcón"},
        {"verb": "oró", "text": "por la revolución", "location": "en la iglesia vieja"},
        {"verb": "pronunció", "text": "un discurso apasionado", "location": "en la plaza del mercado"},
        {"verb": "evangelizó", "text": "sobre la nueva era", "location": "en el parque central"},
    ],
    "organizar": [
        {"verb": "fundó", "text": "un círculo de trabajadores", "location": ""},
        {"verb": "creó", "text": "una red de apoyo mutuo", "location": "en el barrio"},
        {"verb": "estableció", "text": "un comité de autodefensa", "location": "local"},
        {"verb": "organizó", "text": "una assemblea popular", "location": "en la plaza"},
        {"verb": "conformó", "text": "un grupo de acción directa", "location": ""},
        {"verb": "estableció", "text": "una célula clandestina", "location": "en el sótano"},
        {"verb": "creó", "text": "un círculo de debate", "location": "en la biblioteca"},
        {"verb": "fundó", "text": "una cooperativa obrera", "location": ""},
    ],
    "sabotar": [
        {"verb": "sabotó", "text": "los suministros del distrito industrial", "location": ""},
        {"verb": "destruyó", "text": "archivos del régimen", "location": "en la comisaría"},
        {"verb": "interrumpió", "text": "el tráfico en la calle principal", "location": ""},
        {"verb": "sabotó", "text": "la maquinaria de la fábrica", "location": ""},
        {"verb": "incendió", "text": "documentos de deuda", "location": "en el banco"},
        {"verb": "bloqueó", "text": "las rutas de suministro", "location": ""},
        {"verb": "sabotó", "text": "el sistema de comunicaciones", "location": ""},
        {"verb": "destruyó", "text": "los símbolos del viejo orden", "location": ""},
    ],
    "reclutar": [
        {"verb": "reclutó", "text": "3 nuevos miembros para la causa", "location": ""},
        {"verb": "convenció", "text": "a un comerciante local", "location": "de unirse"},
        {"verb": "integró", "text": "a jóvenes al movimiento", "location": ""},
        {"verb": "reclutó", "text": "trabajadores del muelle", "location": ""},
        {"verb": "atrajo", "text": "a intelectuales al círculo", "location": ""},
        {"verb": "reclutó", "text": "artesanos al comité", "location": ""},
        {"verb": "convenció", "text": "a una familia entera", "location": "de joinarse"},
        {"verb": "integró", "text": "a estudiantes en la red", "location": ""},
    ],
    "negociar": [
        {"verb": "negoció", "text": "con los merchants del barrio", "location": ""},
        {"verb": "llegó", "text": "a un acuerdo con los artesanos", "location": ""},
        {"verb": "gestionó", "text": "recursos con comerciantes", "location": ""},
        {"verb": "negoció", "text": "apoyo a cambio de protección", "location": ""},
        {"verb": "medió", "text": "en el conflicto entre facciones", "location": ""},
        {"verb": "concordó", "text": "un trueque con los vendedores", "location": ""},
        {"verb": "negoció", "text": "la liberación de prisioneros", "location": ""},
        {"verb": "acordó", "text": "alianzas con otros grupos", "location": ""},
    ],
}


def get_narrative_action(action: str, archetype: str = "neutral", seed: int | None = None) -> NarrativeAction:
    rng = random.Random(seed)

    templates = NARRATIVE_ACTIONS.get(action, NARRATIVE_ACTIONS["conversar"])
    template = rng.choice(templates)

    return NarrativeAction(
        verb=template["verb"],
        text=template["text"],
        location=template["location"],
    )


def format_narrative_action(npc_name: str, action: str, archetype: str = "neutral", seed: int | None = None) -> str:
    rng = random.Random(seed)
    narrative = get_narrative_action(action, archetype, seed)

    parts = [npc_name, narrative.verb, narrative.text]
    if narrative.location:
        parts.append(narrative.location)

    return " ".join(parts)


def get_preferred_action(archetype: str, seed: int | None = None) -> str:
    from core.domain.registries.archetype_registry import get_archetype
    rng = random.Random(seed)
    archetype_data = get_archetype(archetype)
    preferences = archetype_data.action_preferences.preferred_actions
    return rng.choice(preferences)
