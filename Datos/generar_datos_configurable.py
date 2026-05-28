#!/usr/bin/env python3
"""Genera una instancia con comunas aleatorias de la Región de Valparaíso (región 5).

Ejemplos:
  python generar_datos_configurable.py --comunas 8 --escuelas 3 --seed 42
  python generar_datos_configurable.py --comunas 5 --escuelas 2 --lista "VIÑA DEL MAR,VALPARAISO,QUILPUE"
  python generar_datos_configurable.py --listar-comunas
"""
from __future__ import annotations

import argparse
import os

from generar_datos_core import (
    BASE,
    InstanceConfig,
    comunas_meta_from_keys,
    display_name,
    generate_instance,
    list_communes_available,
    load_all_schools_by_commune,
    normalize,
    sample_communes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera instancia con N comunas aleatorias y K colegios por comuna."
    )
    parser.add_argument(
        "--comunas",
        type=int,
        default=5,
        help="Cantidad de comunas a elegir al azar (default: 5)",
    )
    parser.add_argument(
        "--escuelas",
        type=int,
        default=2,
        help="Top K colegios por matrícula en cada comuna (default: 2)",
    )
    parser.add_argument(
        "--mat-min",
        type=int,
        default=300,
        help="Matrícula mínima para considerar un colegio (default: 300)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semilla para reproducir la muestra aleatoria",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/configurable",
        help="Carpeta de salida relativa a Datos/ (default: data/configurable)",
    )
    parser.add_argument(
        "--lista",
        type=str,
        default=None,
        help="Comunas fijas separadas por coma (ignora --comunas y el sorteo)",
    )
    parser.add_argument(
        "--listar-comunas",
        action="store_true",
        help="Muestra comunas disponibles con colegios y termina",
    )
    return parser.parse_args()


def resolve_commune_keys(args: argparse.Namespace) -> list[str]:
    available = list_communes_available(args.mat_min)
    if args.lista:
        requested = [normalize(x.strip()) for x in args.lista.split(",") if x.strip()]
        schools = load_all_schools_by_commune(args.mat_min)
        keys = []
        for req in requested:
            if req in schools:
                keys.append(req)
                continue
            match = next(
                (k for k in available if normalize(display_name(schools[k][0]["comuna_raw"])) == req),
                None,
            )
            if match:
                keys.append(match)
            else:
                raise ValueError(f"Comuna no encontrada o sin colegios: '{req}'")
        return keys
    return sample_communes(args.comunas, args.mat_min, args.seed)


def main():
    args = parse_args()

    if args.listar_comunas:
        schools = load_all_schools_by_commune(args.mat_min)
        print(f"Comunas disponibles (región 5, mat>={args.mat_min}): {len(schools)}\n")
        for key in sorted(schools.keys(), key=lambda k: display_name(schools[k][0]["comuna_raw"])):
            n = len(schools[key])
            print(f"  {display_name(schools[key][0]['comuna_raw']):25} ({n} colegios)")
        return

    keys = resolve_commune_keys(args)
    meta = comunas_meta_from_keys(keys, load_all_schools_by_commune(args.mat_min))

    output_dir = args.output
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(BASE, output_dir)

    config = InstanceConfig(
        output_dir=output_dir,
        comunas_meta=meta,
        escuelas_por_comuna=args.escuelas,
        mat_min=args.mat_min,
        seed=args.seed,
        etiqueta="configurable_muestra",
    )
    generate_instance(config)


if __name__ == "__main__":
    main()
