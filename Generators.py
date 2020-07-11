import pandas as pd
import numpy as np
import os
from DataExtraction import create_dataset


def get_generator_generic(equation_id, no_samples=1000, input_range=(-100, 100), noise_range=(0,0), master_file="FeynmanEquations.csv"):
    """
    Returns a function gen such that calls to gen return an unpacked tuple X, y for given parameters with no saving or loading

    gen will take in an optional parameter no_samples
    """
    def gen(no_samples=no_samples):
        df = create_dataset(equation_id, no_samples=no_samples, input_range=input_range,save=False, load=False, noise_range=noise_range, master_file=master_file)
        return df.drop("target", axis=1), df['target']
    return gen


def get_generator_pythogoras(no_samples=1000, input_range=(0, 500), to_save=False, save_path="data//"):
    """
    Returns a function gen such that calls to gen return X, y as per pythogoras requirements with saving optional

    gen will take in an optional parameter no_samples
    """
    def gen(no_samples=no_samples):
        inputs = []
        outputs = []

        while len(outputs) < no_samples:
            a = np.random.default_rng().uniform(input_range[0] ,input_range[1])
            b = np.random.default_rng().uniform(input_range[0] ,input_range[1])
            if a == 0 or b == 0:
                continue
            c = np.sqrt(a**2 + b**2)
            if a + b < c:
                continue
            else:
                inputs.append([a, b])
                outputs.append(c)
        c = np.array(outputs)
        df = pd.DataFrame(inputs, columns=["X0", "X1"])
        df['target'] = c
        if to_save:
            df.to_csv(os.path.join(save_path, "pythogoras.csv"), index=False)
        return df.drop('target', axis=1), df['target']
    return gen

def get_generator_resistance(no_samples=1000, input_range=(0, 500), to_save=False, save_path="data//"):
    """
    Returns a function gen such that calls to gen return X, y as per resistance requirements with saving optional

    gen will take in an optional parameter no_samples
    """
    def gen(no_samples=no_samples):
        inputs = []
        outputs = []

        while len(outputs) < no_samples:
            r1 = np.random.default_rng().uniform(input_range[0] ,input_range[1])
            r2 = np.random.default_rng().uniform(input_range[0] ,input_range[1])
            if r1 <= 0 or r2 <= 0 or r1+r2 <=0:
                continue
            r = (r1*r2)/(r1+r2)
            inputs.append([r1, r2])
            outputs.append(r)
        r = np.array(outputs)
        df = pd.DataFrame(inputs, columns=["X0", "X1"])
        df['target'] = r
        if to_save:
            df.to_csv(os.path.join(save_path, "resistance.csv"), index=False)
        return df.drop('target', axis=1), df['target']
    return gen

def get_generator_snell(no_samples=1000, input_range=(0, 1.5708), to_save=False, save_path="data//"):
    """
    Returns a function gen such that calls to gen return X, y as per resistance requirements with saving optional

    gen will take in an optional parameter no_samples
    """
    def gen(no_samples=no_samples):
        inputs = []
        outputs = []
        index = 0
        while index < no_samples:
            i = np.random.default_rng().uniform(input_range[0] ,input_range[1])
            r = np.random.default_rng().uniform(input_range[0] ,input_range[1])
            if -0.0001 <= np.sin(i) <= 0.0001 or -0.0001 <= np.sin(r) <= 0.0001:
                continue
            n = np.sin(i)/np.sin(r)
            inputs.append([i, r])
            outputs.append(n)
            index+=1
        n = np.array(outputs)
        df = pd.DataFrame(inputs, columns=["X0", "X1"])
        df['target'] = n
        if to_save:
            df.to_csv(os.path.join(save_path, "snell.csv"), index=False)
        return df.drop('target', axis=1), df['target']
    return gen