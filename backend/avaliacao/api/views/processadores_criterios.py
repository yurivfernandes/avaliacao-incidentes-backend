from avaliacao.models import NotaCriterioBooleano, NotaCriterioConversao


class ProcessadorCriterioBooleano:
    def processar(self, avaliacao, dados_criterio):
        return NotaCriterioBooleano.objects.create(
            avaliacao=avaliacao,
            criterio_id=dados_criterio['criterio_id'],
            valor=dados_criterio['valor']
        )


class ProcessadorCriterioConversao:
    def processar(self, avaliacao, dados_criterio):
        return NotaCriterioConversao.objects.create(
            avaliacao=avaliacao,
            criterio_id=dados_criterio['criterio_id'],
            conversao_id=dados_criterio['conversao_id']
        )
