# Fluxo da Idea do Interface para gerenciar as regras de normalizacoes

## Configuração do Django para Gerenciamento de Regras
- [ ] Modelos: Defina um modelo NormalizationRule no Django que armazene metadados sobre as regras, como o nome da regra, os campos de origem e destino, e o caminho para os arquivos de regra.
- [ ] Interface para criação/edição: Crie uma interface onde os usuários possam selecionar as variáveis (de RawData) e os campos de destino (de Field), e então gerar automaticamente o diretório e os arquivos da regra.

## Criação Automática de Arquivos e Diretórios

- [ ] Sequenciamento do nome da regra: Use a lógica para sequenciar automaticamente o nome da regra (rule_00001, rule_00002, etc.) no momento da criação.
- [ ] Template inicial do arquivo: Ao criar uma nova regra, gere um arquivo rule.py com um conteúdo inicial baseado nas seleções do usuário.
- [ ] Estrutura de diretório: Crie a estrutura do diretório conforme mostrada na imagem, incluindo __init__.py, description_in.md, description_out.md, e documentation.pdf.

## Visualização e Edição de Arquivos

- [ ] Visualização: Exiba o conteúdo do arquivo rule.py na interface web usando uma caixa de texto ou um editor de código (por exemplo, CodeMirror ou Ace Editor).
- [ ] Edição: Permita que o usuário edite o conteúdo diretamente na interface. As alterações serão salvas de volta no arquivo Python correspondente.
- [ ] Jupyter Notebook: Opcionalmente, integre um notebook Jupyter para permitir edições mais avançadas diretamente no navegador.

## Upload de Documentação
- [ ] Upload de arquivos: Permita que os usuários façam upload de arquivos de documentação diretamente para o diretório da regra. Estes arquivos serão salvos na pasta correspondente, como documentation.pdf.

## Fluxo da Aplicação
- [ ] Tela inicial: Listagem de todas as regras de normalização existentes com opções para criar novas, editar existentes ou excluir.
- [ ] Criação/Edição de Regras: Formulário onde o usuário seleciona variáveis de origem e campos de destino. Após salvar, o sistema cria automaticamente a estrutura da pasta e os arquivos baseados nas seleções.
- [ ] Visualização/Edição: Página de detalhes onde o usuário pode visualizar e editar o conteúdo do arquivo rule.py, com suporte para upload de documentação.
- [ ] Executar a regra: Opcionalmente, você pode permitir que o usuário execute a regra diretamente da interface para testar as transformações.

## Implementação
- [ ] Django Admin: Pode ser feito diretamente no Django Admin, mas para uma interface mais amigável, crie views customizadas com templates.
- [ ] Django Forms: Use forms para capturar as seleções de origem e destino.
- [ ] Code Editor: Integre um editor de código na página de edição, como o Ace Editor.
- [ ] Upload de Arquivos: Use Django Forms ou bibliotecas como django-file-form para upload de arquivos.





### Exemplo de Código

1. **Modelos Django**:

   ```python
   from django.db import models

   class NormalizationRule(models.Model):
       name = models.CharField(max_length=255)
       path = models.CharField(max_length=500)
       source_variables = models.ManyToManyField(Variable, related_name="source_for_rules")
       destination_fields = models.ManyToManyField(Field, related_name="destination_for_rules")
       created_at = models.DateTimeField(auto_now_add=True)

       def save(self, *args, **kwargs):
           if not self.pk:  # creating a new rule
               self.name = self.generate_rule_name()
               self.path = self.create_rule_directory()
               self.create_initial_files()
           super().save(*args, **kwargs)

       def generate_rule_name(self):
           last_rule = NormalizationRule.objects.all().order_by('id').last()
           if not last_rule:
               return "rule_00001"
           rule_number = int(last_rule.name.split('_')[-1]) + 1
           return f"rule_{rule_number:05d}"

       def create_rule_directory(self):
           base_dir = Path(settings.BASE_DIR) / 'normalizations' / self.name
           os.makedirs(base_dir, exist_ok=True)
           return str(base_dir)

       def create_initial_files(self):
           rule_file = Path(self.path) / 'rule.py'
           rule_file.write_text("# Python script for normalization\n\nclass Normalization:\n    def apply(self, df):\n        pass\n")
   ```

2. **View para criar/editar regras**:

   ```python
   from django.shortcuts import render, get_object_or_404
   from django.http import HttpResponseRedirect
   from .models import NormalizationRule
   from .forms import NormalizationRuleForm

   def create_rule(request):
       if request.method == 'POST':
           form = NormalizationRuleForm(request.POST)
           if form.is_valid():
               form.save()
               return HttpResponseRedirect('/rules/')
       else:
           form = NormalizationRuleForm()
       return render(request, 'create_rule.html', {'form': form})

   def edit_rule(request, pk):
       rule = get_object_or_404(NormalizationRule, pk=pk)
       if request.method == 'POST':
           form = NormalizationRuleForm(request.POST, instance=rule)
           if form.is_valid():
               form.save()
               return HttpResponseRedirect('/rules/')
       else:
           form = NormalizationRuleForm(instance=rule)
       return render(request, 'edit_rule.html', {'form': form, 'rule': rule})
   ```

3. **Formulário Django**:

   ```python
   from django import forms
   from .models import NormalizationRule

   class NormalizationRuleForm(forms.ModelForm):
       class Meta:
           model = NormalizationRule
           fields = ['source_variables', 'destination_fields']
   ```
