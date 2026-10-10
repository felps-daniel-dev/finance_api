# Erros de regra de negócio. O service lança estes erros e a rota
# traduz cada um para o status HTTP certo. Assim o service não
# precisa conhecer HTTP.

class NomeDuplicadoError(Exception):
    """Já existe uma conta com esse nome."""


class ContaInativaError(Exception):
    """A operação não é permitida em conta desativada."""


class SaldoInsuficienteError(Exception):
    """O saque é maior que o saldo disponível."""


class ContaComSaldoError(Exception):
    """Não é possível desativar conta com saldo diferente de zero."""