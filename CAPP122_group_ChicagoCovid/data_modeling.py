import datetime
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

database_cross = pd.read_csv("databases/cross_section_database " + \
                      str(datetime.date.today()) + ".csv", index_col = 0)

def do_pca(dataset):
    """
    Calculates principal components and principal axis for a given DataFrame

    Args:
        dataset (Pandas DataFrame): Set of interest

    Returns:
        tuple of DataFrames: (augamented dataset, principal axis)
    """
    
    total_components = 6 # 80% of total variance explained
    comp_names = ["principal_component" + str(x) for x in 
                range(1, total_components + 1)]

    pca_var = [col for col in dataset.columns if not col.startswith('major')]

    ref_df = dataset[pca_var]
    ref_df = StandardScaler().fit_transform(ref_df)

    pca = PCA(n_components = total_components) 
    principal_components = pca.fit_transform(ref_df)
    principal_components = pd.DataFrame(data = principal_components, 
                                        columns = comp_names,
                                        index = dataset.index)

    full_data_frame = pd.concat([dataset, principal_components], axis=1)                                    
    
    principal_axis = pca.components_
    principal_axis = pd.DataFrame(data = principal_axis, 
                                  columns = pca_var)

    return full_data_frame, principal_axis


def best_represented(coord, axes=[0,1], min_cos_2=0.5):
    """
    Taking a principal axes projection, determines which variables
    are better represented in the axes selected, this according to the
    cosine squared indicator.

    Args:
        coord (Pandas DataFrame): Principal Axes
        axes (list, optional): Which axes are being plotted. Defaults to [0,1].
        min_cos_2 (float, optional): Minimal representation quality. 
            Defaults to 0.4.

    Returns:
        str: best represented variables
        
    """

    cos_2 = coord ** 2 / coord.apply(lambda x: sum(x ** 2))
    best_represtented = cos_2.iloc[axes, :].sum() > min_cos_2
    
    return coord.columns[best_represtented]


def fit_model(dep_var, design_matrix, var):
    """
    Given a relevant dataset, this function fits a generalized linear model 
    depending on the characteristics of the dependent variable, selecting along 
    the process an appropriate structure.

    Args:
        dep_var (Pandas Series): Outcome varuable
        design_matrix (Pandas DataFrame): Set with pca
        var (str): name of the dependent variable

    Returns:
        [statsmodels]: Fitted Model
    """
    
    if min(dep_var) >= 0 and max(dep_var) <= 1:
        model = sm.GLM(dep_var, design_matrix, family = sm.families.Binomial())
    else:
        model = sm.OLS(dep_var, design_matrix)

    model_fit = model.fit()
    
    return model_fit


def predict_outcome(dataset, var):
    """
    Produces prediction by majority race by zip code for the outcome variable 
    selected

    Args:
        dataset (Pandas DataFrame): Set of interest
        var (str): name of the dependent variable

    Returns:
        Pandas DataFrame: Predictions 
    """
    
    predictions = {}

    set_with_pca, _ = do_pca(dataset)

    select_vars = [x for x in set_with_pca if x.startswith(("princi", "major"))]
    select_vars.append(var)

    ref_dataset = set_with_pca[select_vars]
    
    depend_var = ref_dataset[var]
    design_matrix = ref_dataset.drop(var, axis=1)
    dummy_position = design_matrix.columns.str.startswith("major")

    model = fit_model(depend_var, design_matrix, var)
    predictions["actual"] = model.predict(design_matrix)

    pred_matrix = design_matrix.copy()
    pred_matrix.loc[:, dummy_position] = 0
    
    races = ["latino", "asian", "black", "white"]
    
    for item in races:
        majority = "majority_" + item 
        race_counterfactual = pred_matrix.copy()
        race_counterfactual[majority] = 1
        predictions[item] = model.predict(race_counterfactual)  

    df = pd.DataFrame(predictions, index = dataset.index)
    df[df < 0] = 0 # Limiting prediction range

    return df