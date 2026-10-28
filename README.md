# comfyui-ace-cover

Custom node pequeno para usar áudio de referência como latent inicial do **ACE-Step 1.5 XL Turbo** no ComfyUI. Ele não depende de RyanOnTheInside, não baixa modelos e não altera o UNET, o guider ou o sampler.

## O que ele faz

`ACE-Step Cover Latent (VAE)` recebe `AUDIO` e o `VAE` do ACE-Step e executa a interface nativa `vae.encode(waveform)`. O `LATENT` resultante é conectado ao `KSampler.latent_image`. O próprio `KSampler.denoise` determina o equilíbrio:

- próximo de `0`: maior preservação da referência;
- `0.65`: ponto de partida usado no workflow de referência;
- próximo de `1`: maior mudança guiada pelo texto.

Isso corresponde ao fluxo de referência fornecido: `LoadAudio → VAEEncodeAudio → KSampler`. A extensão apenas torna o passo de cover explícito, com erros claros para VAE/AUDIO que não sigam a interface do ComfyUI.

## O que deliberadamente não faz

- Não implementa clonagem de voz, separação de stems ou transferência de timbre garantida.
- Não injeta patches internos no ACE-Step nem cria um guider próprio. O workflow de referência usa `ModelSamplingAuraFlow` e `KSampler`; não há evidência local de que outro patch seja exigido. Inventar um patch tornaria a compatibilidade não verificável.
- Não promete que qualquer VAE de terceiros funcione. O nó valida a presença de `encode(waveform)` e retorno `LATENT` com `samples`.

## Instalação no ComfyUI

```bash
cd ComfyUI/custom_nodes
git clone <URL-DO-SEU-REPOSITORIO> comfyui-ace-cover
```

Reinicie o ComfyUI. Não há dependências extras; `requirements.txt` é intencionalmente vazio.

Instale também os arquivos oficiais do ACE-Step nos diretórios do ComfyUI:

- `models/diffusion_models/acestep_v1.5_xl_turbo_bf16.safetensors`
- `models/vae/ace_1.5_vae.safetensors`
- `models/text_encoders/qwen_0.6b_ace15.safetensors`
- `models/text_encoders/qwen_4b_ace15.safetensors`

Importe `workflow/ace_step_1_5_xl_turbo_cover.json`. Se o ComfyUI sinalizar nós ausentes, atualize-o para uma versão que já contenha os nós nativos ACE-Step usados pelo workflow.

## RunPod Serverless

No Dockerfile já usado pelo worker, acrescente antes do `CMD`:

```dockerfile
COPY comfyui-ace-cover /comfyui/custom_nodes/comfyui-ace-cover
```

Ou construa este projeto diretamente com `Dockerfile.runpod` como contexto. Mantenha os pesos em um Network Volume/cache de modelos; eles não fazem parte desta imagem. O endpoint deve ser **Queue-based**. Antes de publicar, execute manualmente o workflow em uma GPU com VRAM suficiente e somente então faça um job curto. Esta extensão não foi executada com os pesos neste ambiente.

## Testes locais

```bash
python -m unittest discover -s tests -v
python -m json.tool workflow/ace_step_1_5_xl_turbo_cover.json > /dev/null
```

Os testes verificam a delegação ao VAE e as mensagens de incompatibilidade. Eles não equivalem a uma geração real: essa validação exige um ComfyUI com os pesos do ACE-Step.
