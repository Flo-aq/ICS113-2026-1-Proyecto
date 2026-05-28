"""Instancia reducida original: 5 comunas del Informe 2, 2 colegios por comuna."""
import os

from generar_datos_core import BASE, InstanceConfig, comunas_meta_informe2, generate_instance

DATA = os.path.join(BASE, "data")
ESCUELAS_POR_COMUNA = 2


def main():
    config = InstanceConfig(
        output_dir=DATA,
        comunas_meta=comunas_meta_informe2(),
        escuelas_por_comuna=ESCUELAS_POR_COMUNA,
        mat_min=300,
        etiqueta="informe2_5_comunas",
    )
    generate_instance(config)


if __name__ == "__main__":
    main()
