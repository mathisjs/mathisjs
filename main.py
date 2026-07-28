import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from stats import (
    get_followers_and_following,
    get_language_percentages,
    get_most_starred_and_forked,
    get_total_commits,
    getpublicandprivate,
)

os = ["Windows", "CachyOS", "MacOS"]
birthday = date(2005, 9, 17)
today = date.today()
years = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
contact = "mathischapeau@proton.me"
font_path = Path(__file__).with_name("fonts") / "DejaVuSansMono.ttf"
themes = {
    "darkmode": {
        "background": "#0d1117",
        "accent": "#ff7b72",
        "heading": "#d2a8ff",
        "muted": "#8b949e",
        "line": "#57606a",
        "text": "#f0f6fc",
        "footer": "#6e7681",
    },
    "lightmode": {
        "background": "#ffffff",
        "accent": "#cf222e",
        "heading": "#8250df",
        "muted": "#656d76",
        "line": "#d0d7de",
        "text": "#1f2328",
        "footer": "#656d76",
    },
}
avatar_ascii = """\
                                #%%%%%%%%##  #%%%#
                          %%%@@@@@%%%%%%%@@@@%%%@@%
                      %%@@@@@@@@@@%%%%%%%%%%%%%%%%@%
                    %@@@@@@@@@@@@%%%%%%%%%%%%%%%%%%@%
                   @@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%%@#
                  %@@@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%@              ##
        #%%%%@@@%%@@@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%         %%@@@@@@%
     %@@@@@@@@@@@@@@@@@@@@@@@@%%%%@@@@@@@@@@@@@@@@@@@@@#     %%@@@@@@@@@@
   %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@##%@@@@@@@@@@@@@%
 %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%@@@@@@@@@@@@@@@@@@@@@@@@#
 @@@@@@@@@@@@@@@@@@@@@@@@@@@#############%%%%%%@@@@@@@@@@@@@@@@@@@@@%#
 @@@@@@@@@@@@@@@@@@@%%%%%%%+---=+***+=-----------===+*#%@@@@@@@@@%#
 #@@@@@@@@@@@@@@@@%%%%%%%%=--+#@%%@@@@@%#**=----=*%@@%##@@@@%%#
   %@@@@@@@@@@@@*==-+*%%%*---=------=+**##%%=--+%#*+=--=%
     #%%@@@@@@@*--=++-=##*-----=+#@@@+=++=-----+%@@@==+#%
          #%%%@+---+**==##---------=------------*+-----=%
               #---#----*#+----------------------*+----+%
                #=--=---+##-----------------------#=---#
                 ##*+=++###*---------------=+++++++---+%
                       #+%###+---------+#%%@@@@@@@%#+-#
                       #-#%####+=----+%@@@%#**++**%@@=%
                       #--#%######*+=@%*=--=+++++=-=*%#
                       %=--+%%%######%*------+++=--=#@
                        #*+--+#@%%######****########%#
                           #*+==*%@@%%############%%
                               #***##%@@%%%%%%%%%#
                                    ###%%%%%#"""


def get_font(size):
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default(size=size)


def fit_text(draw, text, font, max_width):
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text
    while text and draw.textbbox((0, 0), f"{text}…", font=font)[2] > max_width:
        text = text[:-1]
    return f"{text}…"


def draw_leader(draw, label, value, x, y, width, label_font, value_font, theme):
    label = f"{label}:"
    label_width = draw.textbbox((0, 0), label, font=label_font)[2]
    value = fit_text(draw, value, value_font, width - label_width - 34)
    value_width = draw.textbbox((0, 0), value, font=value_font)[2]
    dot_width = draw.textbbox((0, 0), ".", font=label_font)[2]
    dots = "." * max(0, (width - label_width - value_width - 34) // dot_width)
    draw.text((x, y), label, fill=theme["accent"], font=label_font)
    draw.text((x + label_width + 16, y), dots, fill=theme["muted"], font=label_font)
    draw.text((x + width - value_width, y), value, fill=theme["text"], font=value_font)


def draw_section(draw, title, x, y, width, font, theme):
    title = f"- {title} "
    title_width = draw.textbbox((0, 0), title, font=font)[2]
    draw.text((x, y), title, fill=theme["heading"], font=font)
    draw.line((x + title_width, y + 17, x + width, y + 17), fill=theme["line"], width=2)


def draw_languages(image, draw, languages, x, y, label_font, value_font, theme):
    label = "Languages:"
    draw.text((x, y), label, fill=theme["accent"], font=label_font)
    current_x = x + draw.textbbox((0, 0), label, font=label_font)[2] + 18
    for language, percentage in languages:
        icon_name = language.lower().replace("#", "sharp").replace("+", "plus")
        icon_path = Path(__file__).with_name("assets") / "languages" / f"{icon_name}.png"
        if not icon_path.exists():
            continue
        icon = Image.open(icon_path).convert("RGBA")
        image.paste(icon, (current_x, y - 2), icon)
        current_x += 42
        value = f"{percentage}%"
        draw.text((current_x, y + 3), value, fill=theme["text"], font=value_font)
        current_x += draw.textbbox((0, 0), value, font=value_font)[2] + 26


def create_image(private, public, followers, following, most_starred, most_forked, total_commits, language_percentages, theme_name, theme):
    width, height = 1334, 776
    image = Image.new("RGB", (width, height), theme["background"])
    draw = ImageDraw.Draw(image)
    avatar_font = get_font(11)
    header_font = get_font(25)
    label_font = get_font(23)
    value_font = get_font(22)
    section_font = get_font(24)

    starred_name = most_starred["name"] if most_starred else "Aucun dépôt"
    starred_count = most_starred["stargazers_count"] if most_starred else 0
    forked_name = most_forked["name"] if most_forked else "Aucun dépôt"
    forked_count = most_forked["forks_count"] if most_forked else 0

    ascii_height = draw.multiline_textbbox((0, 0), avatar_ascii, font=avatar_font, spacing=4)[3]
    draw.multiline_text((48, (height - ascii_height) // 2), avatar_ascii, fill=theme["muted"], font=avatar_font, spacing=4)

    x = 650
    content_width = 620
    draw.text((x, 42), "mathis1M@github", fill=theme["heading"], font=header_font)
    header_width = draw.textbbox((0, 0), "mathis1M@github", font=header_font)[2]
    draw.line((x + header_width + 18, 60, x + content_width, 60), fill=theme["line"], width=2)

    draw_leader(draw, "OS", ", ".join(os), x, 120, content_width, label_font, value_font, theme)
    draw_leader(draw, "Age", f"{years} years", x, 162, content_width, label_font, value_font, theme)
    draw_leader(draw, "Location", "Brittany, France", x, 204, content_width, label_font, value_font, theme)
    draw_leader(draw, "Hobbies", "Combats Sports, Books and movies", x, 246, content_width, label_font, value_font, theme)

    draw_section(draw, "Contact", x, 300, content_width, section_font, theme)
    draw_leader(draw, "Email", contact, x, 344, content_width, label_font, value_font, theme)

    draw_section(draw, "GitHub Stats", x, 406, content_width, section_font, theme)
    draw_leader(draw, "Repos", f"{public} public, {private} private", x, 450, content_width, label_font, value_font, theme)
    draw_leader(draw, "Followers", f"{followers} followers, {following} following", x, 486, content_width, label_font, value_font, theme)
    draw_leader(draw, "Commits", f"{total_commits} total", x, 522, content_width, label_font, value_font, theme)
    draw_languages(image, draw, language_percentages, x, 558, label_font, value_font, theme)
    draw_leader(draw, "Most starred", f"{starred_name} ({starred_count} stars)", x, 594, content_width, label_font, value_font, theme)
    draw_leader(draw, "Most forked", f"{forked_name} ({forked_count} forks)", x, 630, content_width, label_font, value_font, theme)
    draw.text((x, 724), "inspired by @DietrichGebert", fill=theme["footer"], font=get_font(15))
    image.save(f"readme_{theme_name}.png")


def main():
    private, public = getpublicandprivate()
    followers, following = get_followers_and_following()
    most_starred, most_forked = get_most_starred_and_forked()
    total_commits = get_total_commits()
    language_percentages = get_language_percentages()
    for theme_name, theme in themes.items():
        create_image(private, public, followers, following, most_starred, most_forked, total_commits, language_percentages, theme_name, theme)
    print(json.dumps({
        "private_repos": private,
        "public_repos": public,
        "followers": followers,
        "following": following,
        "total_commits": total_commits,
        "languages": dict(language_percentages),
        "age": years,
        "most_starred": most_starred["name"] if most_starred else None,
        "most_forked": most_forked["name"] if most_forked else None,
    }, indent=4))


if __name__ == "__main__":
    main()
