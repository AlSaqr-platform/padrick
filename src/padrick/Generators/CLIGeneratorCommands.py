import logging
from pathlib import Path

import click
import click_log
from padrick.ConfigParser import parse_config
from padrick.Generators.DocGenerator.DocGenerator import generate_padlist, DocGenException
from padrick.Generators.DriverGenerator.DriverGenerator import generate_driver
from padrick.Generators.RTLGenerator.RTLGenerator import generate_rtl, RTLGenException
from padrick.Generators.TemplateRenderJob import TemplateRenderException
from click import UsageError, ClickException
import os

logger = logging.getLogger("padrick")
click_log.basic_config(logger)


@click.group()
def generate():
    """ Generate various output files for the provided pad_frame configuration"""
    pass

@generate.command()
@click.argument('config_file', type=click.Path(file_okay=True, dir_okay=False, exists=True, readable=True))
@click.option('-o', '--output', type=click.Path(dir_okay=True, file_okay=False), default=".", help="Location where to save the RTL")
@click_log.simple_verbosity_option(logger)
def rtl(config_file: str, output: str):
    """
    Generate SystemVerilog implementation from the padframe configuration.
    """
    logger.info("Parsing configuration file...")
    padframe = parse_config(Path(config_file))
    logger.info("Parsing successful. Generating RTL...")
    if not Path(output).exists():
        logger.debug("Output directory does not exist. Creating new one.")
        os.makedirs(output, exist_ok=True)
    if not padframe:
        raise UsageError("Failed to parse the configuration file")
    try:
        generate_rtl(padframe, Path(output))
    except (RTLGenException, TemplateRenderException) as e:
        raise ClickException("RTL Generation failed") from e
    except Exception as e:
        logger.error("Padrick crashed while generating RTL :-(")
        raise e
    logger.info(f"Successfully generated RTL files in {output}")

@generate.command()
@click.argument('config_file', type=click.Path(file_okay=True, dir_okay=False, exists=True, readable=True))
@click.option('-o', '--output', type=click.Path(dir_okay=True, file_okay=False), default=".", help="Location where to save the driver")
@click_log.simple_verbosity_option(logger)
def driver(config_file: str, output: str):
    """
    Generate C driver to interact with the padframe.
    """
    logger.info("Parsing configuration file...")
    padframe = parse_config(Path(config_file))
    logger.info("Parsing successful. Generating C-Driver...")
    if not Path(output).exists():
        logger.debug("Output directory does not exist. Creating new one.")
        os.makedirs(output, exist_ok=True)
    if not padframe:
        raise UsageError("Failed to parse the configuration file")
    try:
        generate_driver(padframe, Path(output))
    except (RTLGenException, TemplateRenderException) as e:
        raise ClickException("C Driver Generation failed") from e
    except Exception as e:
        logger.error("Padrick crashed while generating the C Driver :-(")
        raise e
    logger.info(f"Successfully generated C driver files in {output}")

@generate.command()
@click.argument('config_file', type=click.Path(file_okay=True, dir_okay=False, exists=True, readable=True))
@click.option('-o', '--output', type=click.Path(dir_okay=True, file_okay=False), default=".", help="Directory where to save the padlist CSV")
def padlist(config_file: str, output: str):
    """
    Generate a CSV file that lists all pads in your configuration.
    """
    logger.info("Parsing configuration file...")
    padframe = parse_config(Path(config_file))
    logger.info("Parsing successful. Generating pad list...")
    if not Path(output).exists():
        logger.debug("Output directory does not exist. Creating new one.")
        os.makedirs(output, exist_ok=True)
    if not padframe:
        raise UsageError("Failed to parse the configuration file")
    try:
        generate_padlist(padframe, Path(output))
    except (DocGenException, TemplateRenderException) as e:
        raise ClickException("Padlist Generation failed") from e
    except Exception as e:
        logger.error("Padrick crashed while generating the padlist :-(")
        raise e
    logger.info(f"Successfully generated the padlist CSV file in {output}")