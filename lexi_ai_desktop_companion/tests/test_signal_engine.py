from app.signal_engine import TemplateSignalEngine


def test_signal_engine_generates_design_signal():
    engine = TemplateSignalEngine()
    signal, metadata = engine.generate_design_signal(
        "core",
        "design Lexi.AI Desktop dashboard with safe control and owner-approved file actions",
    )

    assert "Design Signal" in signal
    assert metadata["domain"] in {
        "desktop companion",
        "AI assistant shell",
        "automation toolkit",
        "science fiction knowledge system",
        "web archive",
        "data dashboard",
    }
    assert metadata["tasks"]
