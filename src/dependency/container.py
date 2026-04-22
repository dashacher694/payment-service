from dependency_injector.containers import WiringConfiguration, copy

from src.dependency.use_case_container import UseCaseContainer


@copy(UseCaseContainer)
class Container(UseCaseContainer):
    wiring_config = WiringConfiguration(
        modules=[
            "src.modules.healthcheck.usecase.check_health.api",
            "src.modules.healthcheck.usecase.check_readiness.api",
            "src.modules.payment.usecase.create_payment.api",
            "src.modules.payment.usecase.get_payment.api",
            "src.modules.outbox.usecase.process_outbox.api",
        ],
    )
