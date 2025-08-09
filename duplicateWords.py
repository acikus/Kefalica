import json
from collections import defaultdict

# Given JSON data
json_data = [
  {
    "columns": {
      "A": {
        "icons": ["apple.png", "banana.png", "orange.png", "grapes.png"],
        "srpski": ["jabuka.png", "banana.png", "pomorandža.png", "grožđe.png"],
        "solution": ["VOĆE"]
      },
      "B": {
        "icons": ["carrot.png", "broccoli.png", "corn.png", "tomato.png"],
        "srpski": ["šargarepa.png", "brokoli.png", "kukuruz.png", "paradajz.png"],
        "solution": ["POVRĆE"]
      },
      "C": {
        "icons": ["icecream.png", "cake.png", "cookie.png", "candy.png"],
        "srpski": ["sladoled.png", "torta.png", "keks.png", "bombona.png"],
        "solution": ["SLATKIŠI","SLATKIŠ","SLATKO"]
      },
      "D": {
        "icons": ["juice.png", "milk.png", "water.png", "smoothie.png"],
        "srpski": ["sok.png", "mleko.png", "voda.png", "smuti.png"],
        "solution": ["PIĆE","PIĆA"]
      }
    },
    "final_solution": ["HRANA","KLOPA"]
  },
  {
    "columns": {
      "A": {
        "icons": ["car.png", "bus.png", "truck.png", "van.png"],
        "srpski": ["auto.png", "autobus.png", "kamion.png", "kombi.png"],
        "solution": ["AUTOMOBILI", "KOLA"]
      },
      "B": {
        "icons": ["bicycle.png", "motorbike.png", "scooter.png", " Segway.png"],
        "srpski": ["bicikl.png", "motor.png", "skuter.png", " Segvej.png"],
        "solution": ["DVOTOČKAŠI"]
      },
      "C": {
        "icons": ["boat.png", "ship.png", "yacht.png", "ferry.png"],
        "srpski": ["brod.png", "brod.png", "jahta.png", "trajekt.png"],
        "solution": ["PLOVILA"]
      },
      "D": {
        "icons": ["airplane.png", "helicopter.png", "jet.png", "drone.png"],
        "srpski": ["avion.png", "helikopter.png", "mlaznjak.png", "dron.png"],
        "solution": ["LETELICE"]
      }
    },
    "final_solution": ["VOZILA", "PREVOZNA SREDSTVA","PREVOZ"]
  },
  {
    "columns": {
      "A": {
        "icons": ["pitcher.png", "bat.png", "glove.png", "base.png"],
        "srpski": ["bacač.png", "palica.png", "rukavica.png", "baza.png"],
        "solution": ["BEJZBOL"]
      },
      "B": {
        "icons": ["basket.png", "hoop.png", "court.png", "jersey.png"],
        "srpski": ["koš.png", "obruč.png", "teren.png", "dres.png"],
        "solution": ["KOŠARKA"]
      },
      "C": {
        "icons": ["ball.png", "goal.png", "field.png", "cleats.png"],
        "srpski": ["lopta.png", "gol.png", "teren.png", "kopačke.png"],
        "solution": ["FUDBAL"]
      },
      "D": {
        "icons": ["serve.png", "racket.png", "net.png", "ace.png"],
        "srpski": ["servis.png", "reket.png", "mreža.png", "as.png"],
        "solution": ["TENIS"]
      }
    },
    "final_solution": ["SPORTOVI","SPORT"]
  },
  {
    "columns": {
      "A": {
        "icons": ["sun.png", "cloud.png", "rainbow.png", "stars.png"],
        "srpski": ["sunce.png", "oblak.png", "duga.png", "zvezde.png"],
        "solution": ["NEBO"]
      },
      "B": {
        "icons": ["tree.png", "flower.png", "grass.png", "leaf.png"],
        "srpski": ["drvo.png", "cveće.png", "trava.png", "list.png"],
        "solution": ["BILJKE"]
      },
      "C": {
        "icons": ["mountain.png", "river.png", "beach.png", "forest.png"],
        "srpski": ["planina.png", "reka.png", "plaža.png", "šuma.png"],
        "solution": ["PRIRODA"]
      },
      "D": {
        "icons": ["rain.png", "snow.png", "wind.png", "lightning.png"],
        "srpski": ["kiša.png", "sneg.png", "vetar.png", "munja.png"],
        "solution": ["VREME"]
      }
    },
    "final_solution": ["ZEMLJA"]
  },
  {
    "columns": {
      "A": {
        "icons": ["pirate.png", "knight.png", "astronaut.png", "folk.png"],
        "srpski": ["pirat.png", "vitez.png", "astronaut.png", "narodni.png"],
        "solution": ["HEROJI","HEROJ","JUNAK","JUNACI"]
      },
      "B": {
        "icons": ["wand.png", "dragon.png", "unicorn.png", "fairy.png"],
        "srpski": ["štapić.png", "zmaj.png", "jednorog.png", "vila.png"],
        "solution": ["MAGIJA","MAGIČNI","ČAROBAN","ČAROBNI"]
      },
      "C": {
        "icons": ["treasure.png", "map.png", "compass.png", "key.png"],
        "srpski": ["blago.png", "mapa.png", "kompas.png", "ključ.png"],
        "solution": ["AVANTURA","AVANTURE"]
      },
      "D": {
        "icons": ["tower.png", "moat.png", "dungeon.png", "throne.png"],
        "srpski": ["kula.png", "šanac.png", "tamnica.png", "presto.png"],
        "solution": ["DVORAC","ZAMAK"]
      }
    },
    "final_solution": ["FANTAZIJA","FANTASTIKA"]
  },
    {
      "columns": {
        "A": {
          "icons": ["sun.png", "beach.png", "pool.png", "icecream.png"],
          "srpski": ["sunce.png", "plaža.png", "bazen.png", "sladoled.png"],
          "solution": ["LETO"]
        },
        "B": {
          "icons": ["snow.png", "gloves.png", "scarf.png", "boots.png"],
          "srpski": ["sneg.png", "rukavice.png", "šal.png", "čizme.png"],
          "solution": ["ZIMA"]
        },
        "C": {
          "icons": ["rain.png", "umbrella.png", "jacket.png", "puddle.png"],
          "srpski": ["kiša.png", "kišobran.png", "jakna.png", "bara.png"],
          "solution": ["JESEN"]
        },
        "D": {
          "icons": ["flower.png", "swallow.png", "garden.png", "awakening.png"],
          "srpski": ["cvet.png", "lasta.png", "bašta.png", "buđenje.png"],
          "solution": ["PROLEĆE"]
        }
      },
      "final_solution": ["GODIŠNJE DOBA", "GODIŠNJA DOBA","DOBA"]
    },
     {
      "columns": {
        "A": {
          "icons": ["book.png", "student.png", "hour.png", "backpack.png"],
          "srpski": ["knjiga.png", "učenik.png", "čas.png", "ranac.png"],
          "solution": ["ŠKOLA","ŠKOLE"]
        },
        "B": {
          "icons": ["desk.png", "chair.png", "blackboard.png", "chalk.png"],
          "srpski": ["klupa.png", "stolica.png", "tabla.png", "kreda.png"],
          "solution": ["UČIONICA","UČIONICE"]
        },
        "C": {
          "icons": ["teacher.png", "student.png", "notebook.png", "eraser.png"],
          "srpski": ["nastavnik.png", "učenik.png", "sveska.png", "gumica.png"],
          "solution": ["NASTAVA","PREDAVANJE"]
        },
        "D": {
          "icons": ["grade.png", "test.png", "diploma.png", "certificate.png"],
          "srpski": ["ocena.png", "test.png", "diploma.png", "svedočanstvo.png"],
          "solution": ["USPEH"]
        }
      },
      "final_solution": ["OBRAZOVANJE"]
    },
    {
      "columns": {
        "A": {
          "icons": ["soccer.png", "basketball.png", "volleyball.png", "tennis.png"],
          "srpski": ["fudbal.png", "košarka.png", "odbojka.png", "tenis.png"],
          "solution": ["SPORT"]
        },
        "B": {
          "icons": ["gold.png", "podium.png", "ribbon.png", "ceremony.png"],
          "srpski": ["zlato.png", "postolje.png", "traka.png", "cermonija.png"],
          "solution": ["MEDALJA"]
        },
        "C": {
          "icons": ["referee.png", "whistle.png", "card.png", "timer.png"],
          "srpski": ["sudija.png", "pištaljka.png", "karton.png", "štoperica.png"],
          "solution": ["SUDIJA"]
        },
        "D": {
          "icons": ["formula.png", "equation.png", "geometry.png", "number.png"],
          "srpski": ["formula.png", "jednačina.png", "geometrija.png", "broj.png"],
          "solution": ["MATEMATIKA"]
        }
      },
      "final_solution": ["TAKMIČENJE"]
    },
    {
      "columns": {
        "A": {
          "icons": ["guitar.png", "piano.png", "drums.png", "violin.png"],
          "srpski": ["gitara.png", "klavir.png", "bubnjevi.png", "violina.png"],
          "solution": ["INSTRUMENT","INSTRUMENTI"]
        },
        "B": {
          "icons": ["rythm.png", "harmony.png", "clef.png", "pitch.png"],
          "srpski": ["ritam.png", "harmonija.png", "ključ.png", "visina_tona.png"],
          "solution": ["NOTA","NOTE"]
        },
        "C": {
          "icons": ["conductor.png", "orchestra.png", "choir.png", "band.png"],
          "srpski": ["dirigent.png", "orkestar.png", "hor.png", "bend.png"],
          "solution": ["IZVOĐAČ","PEVAČ"]
        },
        "D": {
          "icons": ["radio.png", "speaker.png", "headphones.png", "microphone.png"],
          "srpski": ["radio.png", "zvučnik.png", "slušalice.png", "mikrofon.png"],
          "solution": ["ZVUK"]
        }
      },
      "final_solution": ["MUZIKA"]
    },
    {
      "columns": {
        "A": {
          "icons": ["tree.png", "flower.png", "grass.png", "bush.png"],
          "srpski": ["drvo.png", "cvet.png", "trava.png", "žbun.png"],
          "solution": ["BILJKA","BILJKE"]
        },
        "B": {
          "icons": ["dog.png", "cat.png", "bird.png", "fish.png"],
          "srpski": ["pas.png", "mačka.png", "ptica.png", "riba.png"],
          "solution": ["ŽIVOTINJA","ŽIVOTINJE"]
        },
        "C": {
          "icons": ["cloud.png", "rain.png", "sun.png", "wind.png"],
          "srpski": ["oblak.png", "kiša.png", "sunce.png", "vetar.png"],
          "solution": ["VREME"]
        },
        "D": {
          "icons": ["mountain.png", "river.png", "forest.png", "lake.png"],
          "srpski": ["planina.png", "reka.png", "šuma.png", "jezero.png"],
          "solution": ["PEJZAŽ"]
        }
      },
      "final_solution": ["PRIRODA"]
    },
    {
      "columns": {
        "A": {
          "icons": ["brush.png", "canvas.png", "palette.png", "easel.png"],
          "srpski": ["četkica.png", "platno.png", "paleta.png", "štafelaj.png"],
          "solution": ["SLIKANJE"]
        },
        "B": {
          "icons": ["pencil.png", "paper.png", "eraser.png", "sharpener.png"],
          "srpski": ["olovka.png", "papir.png", "gumica.png", "rezač.png"],
          "solution": ["CRTANJE"]
        },
        "C": {
          "icons": ["clay.png", "sculpting.png", "pottery.png", "chisel.png"],
          "srpski": ["glina.png", "vajanje.png", "grnčarija.png", "dleto.png"],
          "solution": ["VAJANJE"]
        },
        "D": {
          "icons": ["camera.png", "film.png", "lens.png", "tripod.png"],
          "srpski": ["kamera.png", "film.png", "objektiv.png", "stativ.png"],
          "solution": ["FOTOGRAFIJA"]
        }
      },
      "final_solution": ["UMETNOST"]
    },
    {
      "columns": {
        "A": {
          "icons": ["car.png", "bus.png", "train.png", "motorcycle.png"],
          "srpski": ["auto.png", "autobus.png", "voz.png", "motor.png"],
          "solution": ["PREVOZ","VOZILO"]
        },
        "B": {
          "icons": ["road.png", "bridge.png", "tunnel.png", "highway.png"],
          "srpski": ["put.png", "most.png", "tunel.png", "autoput.png"],
          "solution": ["PUT"]
        },
        "C": {
          "icons": ["ticket.png", "map.png", "compass.png", "gps.png"],
          "srpski": ["karta.png", "mapa.png", "kompas.png", "navigacija.png"],
          "solution": ["NAVIGACIJA"]
        },
        "D": {
          "icons": ["suitcase.png", "passport.png", "hotel.png", "camera.png"],
          "srpski": ["kofer.png", "pasoš.png", "hotel.png", "fotoaparat.png"],
          "solution": ["PUTOVANJE"]
        }
      },
      "final_solution": ["TURIZAM"]
    },
    {
      "columns": {
        "A": {
          "icons": ["white_coat.png", "nurse.png", "stethoscope.png", "prescription.png"],
          "srpski": ["beli_mantil.png", "sestra.png", "stetoskop.png", "recept.png"],
          "solution": ["LEKAR","DOKTOR"]
        },
        "B": {
          "icons": ["scanner.png", "ambulance.png", "bed.png", "wheelchair.png"],
          "srpski": ["skener.png", "hitna.png", "krevet.png", "kolica.png"],
          "solution": ["BOLNICA"]
        },
        "C": {
          "icons": ["bandage.png", "syringe.png", "thermometer.png", "pills.png"],
          "srpski": ["zavoj.png", "špric.png", "toplomer.png", "lekovi.png"],
          "solution": ["TERAPIJA"]
        },
        "D": {
          "icons": ["heart.png", "lungs.png", "brain.png", "kidney.png"],
          "srpski": ["srce.png", "pluća.png", "mozak.png", "bubreg.png"],
          "solution": ["ORGAN"]
        }
      },
      "final_solution": ["MEDICINA"]
    },
    {
      "columns": {
        "A": {
          "icons": ["monitor.png", "keyboard.png", "mouse.png", "printer.png"],
          "srpski": ["monitor.png", "tastatura.png", "miš.png", "štampač.png"],
          "solution": ["RAČUNAR"]
        },
        "B": {
          "icons": ["phone.png", "tablet.png", "laptop.png", "smartwatch.png"],
          "srpski": ["telefon.png", "tablet.png", "laptop.png", "pametni_sat.png"],
          "solution": ["UREĐAJ"]
        },
        "C": {
          "icons": ["wireless.png", "bluetooth.png", "chemical.png", "radio.png"],
          "srpski": ["bežična.png", "blutut.png", "hemijska.png", "radio.png"],
          "solution": ["VEZA"]
        },
        "D": {
          "icons": ["aplication.png", "game.png", "browser.png", "email.png"],
          "srpski": ["aplikacija.png", "igra.png", "pretraživač.png", "pošta.png"],
          "solution": ["PROGRAM"]
        }
      },
      "final_solution": ["TEHNOLOGIJA"]
    },
    {
      "columns": {
        "A": {
          "icons": ["moon.png", "stars.png", "blue.png", "comet.png"],
          "srpski": ["mesec.png", "zvezde.png", "plava.png", "kometa.png"],
          "solution": ["NEBO"]
        },
        "B": {
          "icons": ["grade.png", "measurement.png", "military .png", "basic.png"],
          "srpski": ["ocena.png", "merna.png", "vojna.png", "osnovna.png"],
          "solution": ["JEDINICA"]
        },
        "C": {
          "icons": ["galaxy.png", "nebula.png", "blackhole.png", "asteroid.png"],
          "srpski": ["galaksija.png", "maglina.png", "crna_rupa.png", "asteroid.png"],
          "solution": ["KOSMOS","SVEMIR","VASIONA"]
        },
        "D": {
          "icons": ["observatory.png", "radar.png", "space.png", "work.png"],
          "srpski": ["opservatorija.png", "radar.png", "svemir.png", "rad.png"],
          "solution": ["STANICA"]
        }
      },
      "final_solution": ["ASTRONOMIJA"]
    }
]


# Function to find duplicate words in solutions
def find_duplicates(data):
    word_counts = defaultdict(int)
    duplicates = defaultdict(list)

    for category in data:
        for column_key, column_value in category["columns"].items():
            for word in column_value["solution"]:
                word_counts[word] += 1
                duplicates[word].append((category["final_solution"], column_key))

        for final_solution in category["final_solution"]:
            word_counts[final_solution] += 1
            duplicates[final_solution].append(("Final", "Final"))

    # Filter duplicates (words appearing more than once)
    duplicate_words = {word: locations for word, locations in duplicates.items() if word_counts[word] > 1}

    return duplicate_words

# Find duplicates
duplicate_words = find_duplicates(json_data)

# Display results
import pandas as pd
from rich import print
df = pd.DataFrame([(word, locations) for word, locations in duplicate_words.items()], columns=["Word", "Occurrences"])


# ... your code to create the DataFrame df ...

print(df)
