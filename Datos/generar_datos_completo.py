#!/usr/bin/env python3
"""Genera instancia completa: todas las comunas de la región 5 con colegios en MINEDUC.

Por defecto incluye TODOS los colegios urbanos activos que cumplan mat-min por comuna.
Use --escuelas N para limitar al top N por matrícula (útil si el modelo es muy pesado).

Ejemplos:
  python generar_datos_completo.py
  python generar_datos_completo.py --escuelas 5 --mat-min 200
  python generar_datos_completo.py --output data/completo
"""
from __future__ import annotations

import argparse
import os

from generar_datos_core import (
    BASE,
    InstanceConfig,
    comunas_meta_from_keys,
    generate_instance,
    list_communes_available,
    load_all_schools_by_commune,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera instancia con todas las comunas de Valparaíso (región 5)."
    )
    parser.add_argument(
        "--escuelas",
        type=int,
        default=None,
        nargs="?",
        const=None,
        help="Top N colegios por comuna. Sin flag = todos los colegios elegibles",
    )
    parser.add_argument(
        "--mat-min",
        type=int,
        default=300,
        help="Matrícula mínima (default: 300). Use 100 para incluir comunas pequeñas",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/completo",
        help="Carpeta de salida (default: data/completo)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    schools = load_all_schools_by_commune(args.mat_min)
    keys = list_communes_available(args.mat_min)
    meta = comunas_meta_from_keys(keys, schools)

    output_dir = args.output
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(BASE, output_dir)

    escuelas = args.escuelas
    total_centros_est = sum(
        min(len(schools[k]), escuelas) if escuelas else len(schools[k]) for k in keys
    )
    print(f"Comunas: {len(keys)} | Centros estimados: {total_centros_est}")

    config = InstanceConfig(
        output_dir=output_dir,
        comunas_meta=meta,
        escuelas_por_comuna=escuelas,
        mat_min=args.mat_min,
        etiqueta="region5_completa",
    )
    generate_instance(config)


if __name__ == "__main__":
    main()
