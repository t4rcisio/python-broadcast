from PIL import Image, ImageDraw
import math
import imageio.v2 as imageio

def gerar_gif_loading_branco(
    filename="loading.gif",
    frame_count=16,  # mais suave
    size=100,
    dot_radius=6,
    circle_radius=30
):
    num_bolinhas = 8
    frames = []

    # Dobra o ciclo para permitir ida/volta suave
    for i in range(frame_count):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Rotação suave
        base_angle = (2 * math.pi * i) / frame_count

        for j in range(num_bolinhas):
            # Calcula a posição de cada bolinha
            angle = base_angle + j * (2 * math.pi / num_bolinhas)
            x = size // 2 + circle_radius * math.cos(angle)
            y = size // 2 + circle_radius * math.sin(angle)

            # Determina a opacidade por ordem (a da frente mais visível)
            relative_index = (j - i) % num_bolinhas
            opacity = int(255 * (relative_index + 1) / num_bolinhas)

            draw.ellipse(
                (x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius),
                fill=(255, 255, 255, opacity)
            )

        frames.append(img)

    # Repete os frames para "voltar ao início" suavemente
    frames += list(reversed(frames))

    # Gera o GIF
    imageio.mimsave(filename, frames, duration=0.08)  # 12.5 FPS

gerar_gif_loading_branco("loading.gif")
