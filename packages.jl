using Pkg

dependencies = [
    "IJulia",
    "BenchmarkTools",
    "StatsKit",
    "Plots",
    "StatsPlots",
    "ModelingToolkit",
    "OrdinaryDiffEq",
    "SteamTables",
    "PyCall",
    "Modia",
    "ForwardDiff",
    "ModiaMath",
    "PlotlyJS",
    "RDatasets",
    "DifferentialEquations",
]

Pkg.add(dependencies)

Pkg.build(dependencies)