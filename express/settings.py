ZERO_WEIGHT_KPOINT_THRESHOLD = 1e-7

SCALAR_PROPERTIES_MANIFEST = {
    "total_energy": {"reference": "express.properties.scalar.total_energy.TotalEnergy"},
    "fermi_energy": {"reference": "express.properties.scalar.fermi_energy.FermiEnergy"},
    "homo_energy": {"reference": "express.properties.scalar.homo_energy.HOMOEnergy"},
    "lumo_energy": {"reference": "express.properties.scalar.lumo_energy.LUMOEnergy"},
    "pressure": {"reference": "express.properties.scalar.pressure.Pressure"},
    "total_force": {"reference": "express.properties.scalar.total_force.TotalForce"},
    "volume": {"reference": "express.properties.scalar.volume.Volume"},
    "density": {"reference": "express.properties.scalar.density.Density"},
    "elemental_ratio": {"reference": "express.properties.scalar.elemental_ratio.ElementalRatio"},
    "p-norm": {"reference": "express.properties.scalar.p_norm.PNorm"},
    "zero_point_energy": {"reference": "express.properties.scalar.zero_point_energy.ZeroPointEnergy"},
    "thermal_correction_to_energy": {
        "reference": "express.properties.scalar.thermal_correction_to_energy.ThermalCorrectionToEnergy"
    },
    "thermal_correction_to_enthalpy": {
        "reference": "express.properties.scalar.thermal_correction_to_enthalpy.ThermalCorrectionToEnthalpy"
    },
    "surface_energy": {"reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"},
    "interfacial_energy": {"reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"},
    "defect_formation_energy": {
        "reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"
    },
    "formation_energy": {"reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"},
    "reaction_energy_barrier": {"reference": "express.properties.scalar.reaction_energy_barrier.ReactionEnergyBarrier"},
    "valence_band_offset": {"reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"},
    "schottky_barrier_height_p": {
        "reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"
    },
    "schottky_barrier_height_n": {
        "reference": "express.properties.scalar.scalar_property_context.ScalarPropertyFromContext"
    },
}

NON_SCALAR_PROPERTIES_MANIFEST = {
    "band_gaps": {"reference": "express.properties.non_scalar.bandgaps.BandGaps"},
    "density_of_states": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.density_of_states.DensityOfStates"
    },
    "band_structure": {"reference": "express.properties.non_scalar.two_dimensional_plot.band_structure.BandStructure"},
    "stress_tensor": {"reference": "express.properties.non_scalar.stress_tensor.StressTensor"},
    "atomic_forces": {"reference": "express.properties.non_scalar.atomic_forces.AtomicForces"},
    "atomic_constraints": {"reference": "express.properties.non_scalar.atomic_constraints.AtomicConstraints"},
    "total_energy_contributions": {
        "reference": "express.properties.non_scalar.total_energy_contributions.TotalEnergyContributions"
    },
    "formation_energy_contributions": {
        "reference": "express.properties.non_scalar.non_scalar_property_context.NonScalarPropertyFromContext"
    },
    "material": {"reference": "express.properties.material.Material"},
    "symmetry": {"reference": "express.properties.non_scalar.symmetry.Symmetry"},
    "workflow:pyml_predict": {"reference": "express.properties.workflow.PyMLTrainAndPredictWorkflow"},
    "phonon_dos": {"reference": "express.properties.non_scalar.two_dimensional_plot.phonon_dos.PhononDOS"},
    "phonon_dispersions": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.phonon_dispersions.PhononDispersions"
    },
    "magnetic_moments": {"reference": "express.properties.non_scalar.magnetic_moments.MagneticMoments"},
    "reaction_energy_profile": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.reaction_energy_profile.ReactionEnergyProfile"
    },
    "potential_profile": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.potential_profile.PotentialProfile"
    },
    "wavefunction_amplitude": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.wavefunction_amplitude.WavefunctionAmplitude"
    },
    "charge_density_profile": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.charge_density_profile.ChargeDensityProfile"
    },
    "file_content": {"reference": "express.properties.non_scalar.file_content.FileContent"},
    "average_potential_profile": {
        "reference": "express.properties.non_scalar.two_dimensional_plot.average_potential_profile.AveragePotentialProfile"  # noqa: E501
    },
    "dielectric_tensor": {"reference": "express.properties.non_scalar.dielectric_tensor.DielectricTensor"},
    "hubbard_u": {"reference": "express.properties.non_scalar.hubbard_u.HubbardU"},
    "hubbard_v": {"reference": "express.properties.non_scalar.hubbard_v.HubbardV"},
    "hubbard_v_nn": {"reference": "express.properties.non_scalar.hubbard_v_nn.HubbardV_NN"},
}

CONVERGENCE_PROPERTIES = {
    "convergence_electronic": {"reference": "express.properties.convergence.electronic.ConvergenceElectronic"},
    "convergence_ionic": {"reference": "express.properties.convergence.ionic.ConvergenceIonic"},
}

PROPERTIES_MANIFEST = dict()
PROPERTIES_MANIFEST.update(CONVERGENCE_PROPERTIES)
PROPERTIES_MANIFEST.update(SCALAR_PROPERTIES_MANIFEST)
PROPERTIES_MANIFEST.update(NON_SCALAR_PROPERTIES_MANIFEST)

PARSERS_REGISTRY = {
    "espresso": "express.parsers.apps.espresso.parser.EspressoParser",
    "vasp": "express.parsers.apps.vasp.parser.VaspParser",
    "nwchem": "express.parsers.apps.nwchem.parser.NwchemParser",
    "q3": "express.parsers.apps.q3.parser.Q3Parser",
    "structure": "express.parsers.structure.StructureParser",
}

# Used to round to zero by default
PRECISION = 9
