#!/usr/bin/env python3
"""
Calculate system temperature (T_sys) and optionally object temperature (T_obj) using calibration measurements.
This script is used for radio astronomy calibration calculations.

Usage:
    ./calculate_calibration.py --t-cal T_CAL --p-cal P_CAL --p-sky P_SKY [--p-obj P_OBJ] [--beam-size BEAM_SIZE --sa-obj SA_OBJ]

Arguments:
    --t-cal: Calibration temperature in Kelvin
    --p-cal: Calibration power
    --p-sky: Sky power
    --p-obj: Object power (optional)
    --beam-size: Beam size in square degrees (optional, required for solid angle correction)
    --sa-obj: Source solid angle in square degrees (optional, required for solid angle correction)

Example:
    ./calculate_calibration.py --t-cal 300 --p-cal 1.5 --p-sky 1.0 --p-obj 1.2 --beam-size 0.1 --sa-obj 0.05
"""

import argparse
import numpy as np
import sys

def calculate_t_sys(t_cal: float, p_cal: float, p_sky: float) -> float:
    """Calculate system temperature using the formula T_sys = T_cal / (p_cal/p_sky - 1)
    
    Args:
        t_cal: Calibration temperature in Kelvin
        p_cal: Calibration power
        p_sky: Sky power
    
    Returns:
        System temperature in Kelvin
    """
    try:
        t_sys = t_cal / (p_cal/p_sky - 1)
        return t_sys
    except ZeroDivisionError:
        raise ValueError("Invalid input: p_cal/p_sky ratio results in division by zero")
    except Exception as e:
        raise ValueError(f"Error calculating T_sys: {str(e)}")

def calculate_t_obj(t_cal: float, p_cal: float, p_sky: float, p_obj: float, beam_size: float = None, sa_obj: float = None) -> float:
    """Calculate object temperature using the formula T_obj = (p_obj-p_sky)/(p_cal-p_sky)*T_cal * (beam_size/sa_obj)^2
    
    Args:
        t_cal: Calibration temperature in Kelvin
        p_cal: Calibration power
        p_sky: Sky power
        p_obj: Object power
        beam_size: Beam size in square degrees (optional)
        sa_obj: Source solid angle in square degrees (optional)
    
    Returns:
        Object temperature in Kelvin
    """
    try:
        t_obj = (p_obj-p_sky)/(p_cal-p_sky)*t_cal
        
        # Apply solid angle correction if both parameters are provided
        if beam_size is not None and sa_obj is not None:
            if sa_obj <= 0:
                raise ValueError("Source solid angle must be greater than zero")
            t_obj *= (beam_size/sa_obj)**2
            
        return t_obj
    except ZeroDivisionError:
        raise ValueError("Invalid input: p_cal-p_sky results in division by zero")
    except Exception as e:
        raise ValueError(f"Error calculating T_obj: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Calculate system temperature (T_sys) and optionally object temperature (T_obj)')
    parser.add_argument('--t-cal', type=float, required=True,
                      help='Calibration temperature in Kelvin')
    parser.add_argument('--p-cal', type=float, required=True,
                      help='Calibration power')
    parser.add_argument('--p-sky', type=float, required=True,
                      help='Sky power')
    parser.add_argument('--p-obj', type=float,
                      help='Object power (optional)')
    parser.add_argument('--beam-size', type=float,
                      help='Beam size in square degrees (optional, required for solid angle correction)')
    parser.add_argument('--sa-obj', type=float,
                      help='Source solid angle in square degrees (optional, required for solid angle correction)')
    
    args = parser.parse_args()
    
    try:
        t_sys = calculate_t_sys(args.t_cal, args.p_cal, args.p_sky)
        print(f"\nInput parameters:")
        print(f"T_cal = {args.t_cal:.2f} K")
        print(f"p_cal = {args.p_cal:.3f}")
        print(f"p_sky = {args.p_sky:.3f}")
        if args.p_obj is not None:
            print(f"p_obj = {args.p_obj:.3f}")
        if args.beam_size is not None:
            print(f"beam_size = {args.beam_size:.3f} deg²")
        if args.sa_obj is not None:
            print(f"sa_obj = {args.sa_obj:.3f} deg²")
        
        print(f"\nCalculated T_sys = {t_sys:.2f} K")
        
        if args.p_obj is not None:
            t_obj = calculate_t_obj(args.t_cal, args.p_cal, args.p_sky, args.p_obj, args.beam_size, args.sa_obj)
            print(f"Calculated T_obj = {t_obj:.2f} K")
            if args.beam_size is not None and args.sa_obj is not None:
                print(f"(including solid angle correction factor: {(args.beam_size/args.sa_obj)**2:.3f})")
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 