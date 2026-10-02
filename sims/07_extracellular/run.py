#!/usr/bin/env python

r"""
.. _tutorial-ecg:

Overview
========

This example explains the background of computing extracellular potentials and electrocardiograms (ECGs) using different techniques.
The techniques used have their specific advantages depending on the application scenario.
In this example the focus is on using :math:`\phi_{\rm e}` to compute unipolar extracellular electrograms
and compare these with fullblown bidomain simulations.

*  **Recovery of extracellular potentials:** 
   Recovery techniques are efficient when potentials shall be computed
   for a limited number of field points. An important limitation is the underlying assumption
   that cardiac electric sources are immersed in an unbounded conductive medium of conductivity :math:`\sigma_\mathrm{b}`.
   The technique is not overly efficient for a large number of field points such as in a 
   body surface potential mapping application. There BEM-based or lead field approaches are better suitable.

*  **bidomain:**
   When using a bidomain formulation, extracellular current flow and potentials are computed everywhere in the entire domain.
   This approach is most accurate and considered a gold standard for ECG modeling.
   However, the main disadvantage is the significantly increased computational cost.
   First, the entire domain must be explicitly discretized, that is, the tissue domain plus a bath or torso domain
   where extracellular potentials can be recorded.
   Secondly, bidomain requires the solution of an elliptic PDE which tends to be more costly 
   than the plain reaction-diffusion monodomain equation, roughly by one order of magnitude.

*  **pseudo bidomain:**
   In this case very similar considerations hold as in the bidomain case. The main advantage of a pseudo-bidomain approach
   as published by `Bishop & Plank <https://www.ncbi.nlm.nih.gov/pubmed/21292591>`_ are the significant savings in computational cost.
   A pseudo-bidomain is only marginally more expensive than a monodomain simulation 
   as extracellular potentials are only solved at output granularity.
   The main disadvantage of the pseudo-bidomain approach is that any feedback of current flow in the extracellular medium
   upon excitation spread remains unaccounted for.

Theoretical background and more rigorous validation of the methods are found in [#bishopaugment]_ and [#bishopecg]_.

To run the experiments of this example, change directories as follows:

.. code-block:: bash

   cd ${EXAMPLES}/02_EP_tissue/07_extracellular


Objectives
==========

This example aims to achieve the following objectives:

* Understand how to use the openCARP :math:`\phi_{\rm e}`-recovery feature

* Analyse differences between  :math:`\phi_{\rm e}`-recovery and full bidomain-based extracellular potentials

* Examine the effect of bath size upon extracellular potentials in the bath medium 
  and its relationship to recovered potentials.


Setup
=====

A simple reduced wedge setup is used for this example.
While a reasonable transmural width of 10 mm is used, in the circumferential direction
the spatial extent is limited to the used spatial resolution for the sake of computational efficiency.
That is, the wedge is a 3D object, but comprises only one layer of elements 
along the circumferential direction (x-axis), rendering the setup almost 2D.
The wedge contains transmural as well as apico-basal heterogeneities
which are based on the study of Boukens et al [#boukenswedge]_.
The wedge uses standard transmural fiber rotation.
Stimulation sites to initiate propagation can be chosen at six different locations
along the endocardial and epicardial surface.
The size of the bath is exposed as an input parameter and can be varied.
An overview of the experimental setup is given in the `ECG setup figure <fig-tutorial-ecg_>`_ A).
Default visualization outputs showing local activation time, action potential propagation
and extracellular potentials are illustrated in the `ECG setup figure <fig-tutorial-ecg_>`_ B).

.. _fig-tutorial-ecg:

.. figure:: /images/02_07_extPotentials_ECG.png
    :name: fig-tutorial-ecg
    :width: 90%
    :align: center

    Computing extracellular potentials and ECGs. A) Setup  B) Visualization
    Extracellular potentials :math:`\phi_{\mathrm 0} - \phi_{\mathrm 6}` are recovered
    at the indicated locations along the apico-basal centerline to be compared with bidomain-based potentials.
    Three recovery sites are located inside the tissue, one in the midmyocardium,
    and one at endocardial and epicardial surfaces, respectively.
    In the presence of a bath (i.e., ``bath>0``) extra recovery sites are located
    at the surface of the bath and in the center of the bath for both bath compartments
    interfacing with endocardial and epicardial surfaces.


Input parametes
===============

The following input parameters are exposed to steer the experiment:
 
::
 
  --duration DURATION     
                          Duration of simulation [ms].
                          Choosing a value of around 70 ms covers activation only
                          and thus yields only the depolarization complex of the ECG.
                          A value of 350 ms covers also repolarization and T-waves.

  --resolution RESOLUTION
                          choose mesh resolution in [um] (default is 250 um).

  --tm-stim-location {endo,epi}

                           choose transmural stimulus location (default is endo)
  
  --ab-stim-location {apex,mid,base}

                           choose apicobasal stimulus location (default is mid)

  --bath BATH           
                           choose size of bath to attach at epi and endo [mm]
                           (default is 0.0 mm). With increasing the bath size
                           the difference between recovered extracellular potentials 
                           and (pseudo-)bidomain potentials diminishes.

  --sourceModel {monodomain,bidomain,pseudo_bidomain}

                           pick type of electrical source model (default is monodomain).
                           For comparing, pseudo_bidomain is most appropriate 
                           as compute time with bidomain is markedly longer.
  

Expected results
================

In the monodomain case where we do not compute potentials in the bath domain, only recovered extracellular potentials
can be inspected. In the `monodomain ECG figure <fig-tutorial-ecg-monodomain_>`_ expected results are illustrated.
Recovered extracellular potentials and corresponding field points are shown. 

.. _fig-tutorial-ecg-monodomain:

.. figure:: /images/02_07_unipolar_electrograms_ini_uni_term.png
   :width: 100%
   :align: center

   Visualization of recovered extracellular potentials at sites of 
   initiating propagation (:math:`\phi_{\rm 0}` in the `ECG setup figure <fig-tutorial-ecg_>`_ B),
   uniform undisturbed propagation  (:math:`\phi_{\rm 1}` in the `ECG setup figure <fig-tutorial-ecg_>`_ B) 
   and terminating (or colliding) propagation  (:math:`\phi_{\rm 2}` in the `ECG setup figure <fig-tutorial-ecg_>`_ B). 
   

Activation spread in terms of transmembrane voltage :math:`V_{\rm m}` and extracellular potential :math:`\phi_{\rm e}`
are shown in the `excitation spread figure <fig-tutorial-ecg-excitation-spread_>`_.

.. _fig-tutorial-ecg-excitation-spread:

.. figure:: /images/02_07_wedge_ecg.gif
   :width: 75%
   :align: center

   Action potential propagation is elicited at the endocardial apical edge of the wedge. 
   The spread of activation and repolarization is shown 
   in terms of extracellular potential :math:`\phi_{\rm e}` and transmembrane voltage :math:`V_{\rm m}`.
   Field points at which extracellular potentials were recovered are shown in the right panel.


Experiments
===========

.. _exp-em-ti-ecg-01:

**Experiment exp01 (central endocardial activation (monodomain) with ecg recovery)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In a first step we omit a bath and use a *monodomain* as a source model. Extracellular potentials are computed
using the :math:`\phi_{\rm e}` recovery technique. 
Propagation is initiated at the center of the endocardial surface as if activated by a Purkinje fascicle.
Only 60 ms of activation are computed as we are only interested in the depolarization complex.

.. code-block:: bash

   ./run.py --sourceModel monodomain --duration 60 --visualize

In this case, the extracellular potentials at the sites of stimulus delivery (vertex 0, initiating propagation),
in the mid-myocardium (vertex 1, undisturbed uniform propagation)
and at the epicardial surface (vertex 2, terminating propagation) shall be examined.


.. _exp-em-ti-ecg-02:

**Experiment exp02 (apical endocardial activation (monodomain) with ecg recovery)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In experiment exp02 we shift the stimulus towards the apical edge of the wedge at the endocardium.
The observation sites for recovering :math:`\phi_{\rm e}` remain the same, 
but local activation patterns underneath the recording electrodes are changed.
This is reflected in the waveforms of the unipolar extracellular electrograms.
Total activation time in this case is longer, which is why we pick a larger duration
to allow for the entire wedge being activated.

.. code-block:: bash

   ./run.py --ab-stim-location apex --sourceModel monodomain --duration 100 --visualize


.. _exp-em-ti-ecg-03:

**Experiment exp03 (apical endocardial activation (pseudo-bidomain) with ecg recovery, small bath)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We repeat `exp02 <exp-em-ti-ecg-02_>`_ using a pseudo-bidomain source model. 
This allows the comparison between extracellular potentials computed by the bidomain method
with those computed by the recovery method. 
We start with a very small bath size of only 1 mm.


.. code-block:: bash

   ./run.py --ab-stim-location apex --sourceModel pseudo_bidomain --bath 1.0 --duration 60 --visualize


.. _exp-em-ti-ecg-04:

**Experiment exp04 (apical endocardial activation (pseudo-bidomain) with ecg recovery, larger bath)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We repeat `exp03 <exp-em-ti-ecg-03_>`_ using a larger bath of 20 mm width
to examine how bath size effects extracellular potential waveforms, their magnitude 
and differences between bidomain and recovery potentials. 


.. code-block:: bash

   ./run.py --ab-stim-location apex --sourceModel pseudo_bidomain --bath 20.0 --duration 60 --visualize


.. _exp-em-ti-ecg-05:

**Experiment exp05 (apical endocardial activation (monodomain) with ecg recovery, repolarization)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We repeat `exp02 <exp-em-ti-ecg-02_>`_, but run for longer to observe unipolar electrograms during repolarization. 

.. code-block:: bash

   ./run.py --ab-stim-location apex --sourceModel monodomain --duration 400 --visualize

In this case it is of interest to examine so-called transmural ECGs, that is, the difference
between unipolar electrograms recorded from endocardial and epicardial surfaces. 
The recovered unipolar ECG traces are stored in the file phie_recovery.igb in igb-format
in the respective output directories. We use ``igbextract`` to compute the differences from the igb file
and store the output in a text file for easier visualization. For this end we run:

.. code-block:: bash

   ./run.py --tmECG simID


where ``simID`` is the name of the output directory for which we want to compute the transmural ECG.    
The computed transmural ECG can be visualized, for instance, with gnuplot.


.. rubric:: References

.. [#bishopaugment]  *Bishop MJ, Plank G.*,
                     **Representing cardiac bidomain bath-loading effects by an augmented monodomain approach: 
                     application to complex ventricular models.**, 
                     IEEE Trans Biomed Eng 58(4):1066-75, 2011.
                     `[Pubmed] <https://www.ncbi.nlm.nih.gov/pubmed/21292591>`__
                     `[PMC] <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3075562/>`__


..  [#bishopecg]     *Bishop MJ, Plank G.*
                     **Bidomain ECG simulations using an augmented monodomain model for the cardiac source.**
                     IEEE Trans Biomed Eng 58(8):2297-2307, 2011.
                     `[Pubmed] <https://www.ncbi.nlm.nih.gov/pubmed/21536529>`__
                     `[PMC] <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3378475/>`__

..  [#boukenswedge]  *Boukens B,  Sulkin MS, Gloschat CR, Ng FS, Vigmond EJ, Efimov IR.*
                     **Transmural APD gradient synchronizes repolarization in the human left ventricular wall.**
                     Cardiovasc Res 108(1):188-96, 2015. 
                     `[Pubmed] <https://www.ncbi.nlm.nih.gov/pubmed/26209251>`__
                     `[PMC] <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4571834/>`__

"""
import os

from carputils.model import Stimulus, ConductivityRegion, optionlist
from carputils.model.lat import Lat

EXAMPLE_DESCRIPTIVE_NAME = 'Extracellular potentials and ECGs'
EXAMPLE_AUTHOR = 'Gernot Plank <gernot.plank@medunigraz.at>, Fernando Campos <fernando.campos@kcl.ac.uk>'
EXAMPLE_DIR = os.path.dirname(__file__)
CALLER_DIR = os.getcwd()
GUIinclude = False

from datetime import date
from carputils import settings
from carputils import tools
from carputils import mesh
from carputils import ep
from carputils.carpio import txt
import numpy as np
import matplotlib.pyplot as plt


def parser():
    parser = tools.standard_parser()
    group = parser.add_argument_group('experiment specific options')

    group.add_argument('--duration',
                       type = float, default = 100.,
                       help = 'Duration of simulation (default is %(default)s ms)')
    group.add_argument('--resolution',
                       type = float, default = 250.,
                       help = 'choose mesh resolution in [um] (default is %(default)s um)')
    group.add_argument('--tm-stim-location',
                       choices = ['endo', 'epi'],
                       default = 'endo',
                       help='choose transmural stimulus location (default is %(default)s)')
    group.add_argument('--ab-stim-location',
                       choices = ['apex', 'mid', 'base'],
                       default = 'mid',
                       help = 'choose apicobasal stimulus location (default is %(default)s)')
    group.add_argument('--bath',
                       type = float, default = 0.,
                       help='choose size of bath to attach at epi and endo (default is %(default)s mm)')
    group.add_argument('--sourceModel',
                       default = 'monodomain',
                       choices = ep.MODEL_TYPES,
                       help = 'pick type of electrical source model (default is %(default)s)')
    group.add_argument('--tmECG',
                       type = str, default = None,
                       help = 'provide simID for which to compute the transmural ECG')
    group.add_argument('--GNa',
                       type = float, default = 1.,
                       help = 'factor to modify sodium conductance (default is %(default)s)')
    group.add_argument('--conductivity',
                       type = float, default = 1.,
                       help = 'factor to modify tissue conductivity (default is %(default)s)')
    return parser


def jobID(args):
    """
    Generate name of top level output directory.
    """
    today = date.today()
    return f'{today.isoformat()}_ecg_{args.resolution}_um_{args.sourceModel}_tm_{args.tm_stim_location}_ab_{args.ab_stim_location}_dur_{args.duration}_ms'



@tools.carpexample(parser, jobID, clean_pattern=r'^(\d{4}-\d{2}-\d{2})|(mesh)|(.pts)')
def run(args, job):
    UM2MM = 1e-3    # convert microns into mm


    if args.tmECG is not None:
        vtx_endo = 0
        vtx_epi  = 2

        compute_tmECG(args.tmECG, vtx_endo, vtx_epi, job,args.webGUI,args.ID)
        return

    # Generate mesh
    # Size of the wedge (mm)
    wedge_x = args.resolution * UM2MM
    wedge_y = 50
    wedge_z = 10
    wedgeSz = [wedge_x, wedge_y, wedge_z]

    # build mesh and tags
    meshname, geom, tags = build_wedge(wedgeSz, args)

    # query for element tags
    _, etags,_ = txt.read(meshname + '.elem')
    etags = np.unique(etags)
    IntraTags = etags[etags != 0]   # element labels for extracellular grid
    ExtraTags = etags.copy()        # element labels for intracellular grid

    # set up ionic heterogeneity
    imp_reg = ionic_setup(tags, args.GNa)

    # set up conductive heterogeneity (not used)
    g_reg = setup_gregions(tags, args.conductivity)

    # set up stimulation
    stim = setup_stimulus(geom, args)
  
    # LATs
    lat = setup_lats()

    # ECG
    writeECGgrid(wedgeSz, args.bath)

    # recover phie's at given locations
    ecg = ['-phie_rec_ptf', os.path.join(CALLER_DIR, 'ecg')]

    # Determine model type
    srcmodel = ep.model_type_opts(args.sourceModel)

    # NUMERICAL PARAMETERS
    num_par = ['-dt',        100,
               '-parab_solve', 1]

    # I/O
    IO_par = ['-spacedt', 0.1,
              '-timedt',  1.0]


    # Get basic command line, including solver options
    cmd = tools.carp_cmd()

    cmd += imp_reg
    cmd += num_par
    cmd += IO_par
    cmd += ecg
    cmd += srcmodel
    cmd += optionlist([stim, lat]+g_reg)
    cmd += tools.gen_physics_opts(ExtraTags=ExtraTags, IntraTags=IntraTags)

    cmd += ['-meshname', meshname,
            '-tend',     args.duration,
            '-simID',    job.ID]

    if args.visualize:
        cmd += ['-gridout_i', 3,
                '-gridout_e', 3]

    # Run simulation 
    job.carp(cmd, 'Extracellular potentials and ECGs')
    
    # Do visualization
    if args.visualize and not settings.platform.BATCH:

        # Prepare file paths
        geom = os.path.join(job.ID, os.path.basename(meshname)+'_i')

        # show lats
        data = os.path.join(job.ID, 'init_acts_LATs-thresh.dat')
        view = os.path.join(EXAMPLE_DIR, 'view_lat.mshz')
        
        # Visualize with webGUI
        if args.webGUI:
            folderNameExp = f'/experiments/07_extracellular_{job.ID}'
            os.mkdir(folderNameExp)
            cmdMesh = f'meshtool collect -imsh={geom} -omsh={folderNameExp}/{job.ID} -nod={data} -ifmt=carp_txt -ofmt=ens_bin'
            outMesh = os.system(cmdMesh)
            if(outMesh == 0):
                print('Meshtool - conversion successfully')
            else:
                print('Meshtool - conversion failure')
        
        #Visualize with meshalyzer
        else:
            # Call meshalyzer to show activation isochrones 
            job.meshalyzer(geom, data, view)

        # transmembrane voltage
        data = os.path.join(job.ID, 'vm.igb')
        view = os.path.join(EXAMPLE_DIR, 'view_vm.mshz')

        # load auxilliary data
        aux = os.path.join(job.ID, 'ecg.pts_t')

        # actually we still need to create the files in a postprocessing step
        # Note: produces the same results as the former '-dump_ecg_leads' flag!
        recv_ptsFile = os.path.join(CALLER_DIR, 'ecg.pts')
        recv_igbFile = os.path.join(job.ID, 'phie_recovery.igb')
        txt.write(aux, recv_igbFile, ptsf=recv_ptsFile)

        # Visualize with webGUI
        # Need review aux in meshtool collect?
        if args.webGUI:
            cmdMesh = f'meshtool collect -imsh={geom} -omsh={folderNameExp}/{job.ID}_Vm -nod={data} -ifmt=carp_txt -ofmt=ens_bin'
            outMesh = os.system(cmdMesh)
            if(outMesh == 0):
                print('Meshtool - conversion successfully')
            else:
                print('Meshtool - conversion failure')
        
        #Visualize with meshalyzer
        else:
            # Call meshalyzer to show Vm
            job.meshalyzer(geom, data, aux, view)

        # load recovered potentials and ecg field points
        geom = os.path.join(CALLER_DIR, 'ecg.pts')
        data = os.path.join(job.ID, 'phie_recovery.igb')
        view = os.path.join(EXAMPLE_DIR, 'view_phie_recovery.mshz')
        
        # Visualize with webGUI
        # Need review meshtool collect failed with missing file ecg.elem
        if args.webGUI:
            geom = os.path.join(job.ID, os.path.basename(meshname)+'_i')
            cmdMesh = f'meshtool collect -imsh={geom} -omsh={folderNameExp}/{job.ID}_ExtraCellPotential -nod={data} -ifmt=carp_txt -ofmt=ens_bin'
            outMesh = os.system(cmdMesh)
            if(outMesh == 0):
                print('Meshtool - conversion successfully')
            else:
                print('Meshtool - conversion failure')
            
        #Visualize with meshalyzer
        else:
            # Call meshalyzer to show recovered extracellular potentials
            job.meshalyzer(geom, data,aux, view)


        if 'bidomain' in args.sourceModel:
            geom = os.path.join(job.ID, os.path.basename(meshname)+'_e')
            data = os.path.join(job.ID, 'phie.igb')
            view = os.path.join(EXAMPLE_DIR, 'view_phie.mshz')

             # Visualize with webGUI
            if args.webGUI:
                cmdMesh = f'meshtool collect -imsh={geom} -omsh={folderNameExp}/{job.ID}_Vm_Bidomain -nod={data} -ifmt=carp_txt -ofmt=ens_bin'
                outMesh = os.system(cmdMesh)
                if(outMesh == 0):
                    print('Meshtool - conversion successfully')
                else:
                    print('Meshtool - conversion failure')
            
            #Visualize with meshalyzer
            else:
                # Call meshalyzer to show Vm
                job.meshalyzer(geom, data, view)


def build_wedge(wedgeSz,args):
    """
    Build a thin transmural wedge preparation with tagging for the assignment
    of transmural as well as apicobasal heterogeneities.
    """

    wedge_x = wedgeSz[0]
    wedge_y = wedgeSz[1]
    wedge_z = wedgeSz[2]
    h = wedge_x

    geom = mesh.Block(size=(wedge_x,wedge_y,wedge_z), resolution=h, etype='tetra')
   
    # attach bath to endo and epi
    bath_z  = args.bath
    geom.set_bath(thickness=(0,0,bath_z), both_sides=True)

    # Transmural gradient
    endo = 3.5
    mid  = 4.0
    epi  = wedge_z - endo - mid
    
    # Apico-basal gradient
    apex    = 15
    central = 20
    base    = wedge_y - central - apex
    
    # Tags
    tag_apex_endo    = 300 + 25
    tag_apex_mid     = 300 + 50
    tag_apex_epi     = 300 + 75
    
    tag_central_endo = 200 + 25
    tag_central_mid  = 200 + 50
    tag_central_epi  = 200 + 75
    
    tag_base_endo    = 100 + 25
    tag_base_mid     = 100 + 50
    tag_base_epi     = 100 + 75
    
    # Add regions ------> (0,0,0) is the center of the mesh, not the left lower corner!
    epi_z0 = -wedge_z/2
    epi_z1 =  epi_z0 + epi
    
    mid_z0 = epi_z1
    mid_z1 = mid_z0 + mid

    endo_z0 = mid_z1
    endo_z1 = endo_z0 + endo
    
    # Apex is the lower part of the wedge
    apex_y0 = -wedge_y/2
    apex_y1 =  apex_y0 + apex
    
    central_y0 = apex_y1
    central_y1 = central_y0 + central
    
    base_y0 = central_y1
    base_y1 = base_y0 + base
    
    # Create mesh
    apex_endo = mesh.BoxRegion((-wedge_x, apex_y0,endo_z0),(wedge_x,apex_y1,endo_z1),tag_apex_endo)
    geom.add_region(apex_endo)
    apex_mid  = mesh.BoxRegion((-wedge_x, apex_y0,mid_z0 ),(wedge_x,apex_y1,mid_z1 ),tag_apex_mid)
    geom.add_region(apex_mid)
    apex_epi  = mesh.BoxRegion((-wedge_x, apex_y0,epi_z0 ),(wedge_x,apex_y1,epi_z1 ),tag_apex_epi)
    geom.add_region(apex_epi)
    
    central_endo = mesh.BoxRegion((-wedge_x,central_y0,endo_z0),(wedge_x,central_y1,endo_z1),tag_central_endo)
    geom.add_region(central_endo)
    central_mid  = mesh.BoxRegion((-wedge_x,central_y0,mid_z0 ),(wedge_x,central_y1,mid_z1 ),tag_central_mid)
    geom.add_region(central_mid)
    central_epi  = mesh.BoxRegion((-wedge_x,central_y0,epi_z0 ),(wedge_x,central_y1,epi_z1 ),tag_central_epi)
    geom.add_region(central_epi)

    base_endo = mesh.BoxRegion((-wedge_x,base_y0,endo_z0),(wedge_x,base_y1,endo_z1),tag_base_endo)
    geom.add_region(base_endo)
    base_mid  = mesh.BoxRegion((-wedge_x,base_y0,mid_z0 ),(wedge_x,base_y1,mid_z1 ),tag_base_mid)
    geom.add_region(base_mid)
    base_epi  = mesh.BoxRegion((-wedge_x,base_y0,epi_z0 ),(wedge_x,base_y1,epi_z1 ),tag_base_epi)
    geom.add_region(base_epi)
    
    # Set fibre angle to 0, sheet angle to 0
    geom.set_fibres(60,-60, 0, 0)
    
    # Generate and return base name
    meshname = mesh.generate(geom)

    # build tag dictionary
    tags = {'tag_apex_endo'   : tag_apex_endo,
            'tag_apex_mid'    : tag_apex_mid,
            'tag_apex_epi'    : tag_apex_epi,
            'tag_central_endo': tag_central_endo,
            'tag_central_mid' : tag_central_mid,
            'tag_central_epi' : tag_central_epi,
            'tag_base_endo'   : tag_base_endo,
            'tag_base_mid'    : tag_base_mid,
            'tag_base_epi'    : tag_base_epi }

    return meshname, geom, tags
   

def ionic_setup(tags,GNa):
    """
    Set up heterogeneities in ionic properties
    """
    imp_reg = ['-num_imp_regions',        9,
               '-imp_region[0].im',       'tenTusscherPanfilov',
               '-imp_region[0].im_param', f'flags=ENDO,GKs*0.45,GNa*{GNa}',
               '-imp_region[0].name',     'VE-BASE-ENDO',
               '-imp_region[0].num_IDs',  1,
               '-imp_region[0].ID[0]',    tags['tag_base_endo'],
               '-imp_region[1].im',       'tenTusscherPanfilov',
               '-imp_region[1].im_param', f'flags=MCELL,GKs*2.48,GNa*{GNa}',
               '-imp_region[1].name',     'VE-BASE-MCELL',
               '-imp_region[1].num_IDs',  1,
               '-imp_region[1].ID[0]',    tags['tag_base_mid'],
               '-imp_region[2].im',       'tenTusscherPanfilov',
               '-imp_region[2].im_param', f'flags=EPI,GKs*0.86,GNa*{GNa}',
               '-imp_region[2].name',     'VE-BASE-EPI',
               '-imp_region[2].num_IDs',  1,
               '-imp_region[2].ID[0]',    tags['tag_base_epi'],
               '-imp_region[3].im',       'tenTusscherPanfilov',
               '-imp_region[3].im_param', f'flags=ENDO,GKs*0.56,GNa*{GNa}',
               '-imp_region[3].name',     'VE-CENTRAL-ENDO',
               '-imp_region[3].num_IDs',  1,
               '-imp_region[3].ID[0]',    tags['tag_central_endo'],
               '-imp_region[4].im',       'tenTusscherPanfilov',
               '-imp_region[4].im_param', f'flags=MCELL,GKs*3.1,GNa*{GNa}',
               '-imp_region[4].name',     'VE-CENTRAL-MCELL',
               '-imp_region[4].num_IDs',  1,
               '-imp_region[4].ID[0]',    tags['tag_central_mid'],
               '-imp_region[5].im',       'tenTusscherPanfilov',
               '-imp_region[5].im_param', f'flags=EPI,GKs*1.1,GNa*{GNa}',
               '-imp_region[5].name',     'VE-CENTRAL-EPI',
               '-imp_region[5].num_IDs',  1,
               '-imp_region[5].ID[0]',    tags['tag_central_epi'],
               '-imp_region[6].im',       'tenTusscherPanfilov',
               '-imp_region[6].im_param', f'flags=ENDO,GKs*0.67,GNa*{GNa}',
               '-imp_region[6].name',     'VE-APEX-ENDO',
               '-imp_region[6].num_IDs',  1,
               '-imp_region[6].ID[0]',    tags['tag_apex_endo'],
               '-imp_region[7].im',       'tenTusscherPanfilov',
               '-imp_region[7].im_param', f'flags=MCELL,GKs*3.72,GNa*{GNa}',
               '-imp_region[7].name',     'VE-APEX-MCELL',
               '-imp_region[7].num_IDs',  1,
               '-imp_region[7].ID[0]',    tags['tag_apex_mid'],
               '-imp_region[8].im',       'tenTusscherPanfilov',
               '-imp_region[8].im_param', f'flags=EPI,GKs*1.29,GNa*{GNa}',
               '-imp_region[8].name',     'VE-APEX-EPI',
               '-imp_region[8].num_IDs',  1,
               '-imp_region[8].ID[0]',    tags['tag_apex_epi'] ]
    return imp_reg


def setup_gregions(tags, conductivity):
    """
    Setup heterogeneities in conductivity
    """
    gi = 0.174 * conductivity
    endo_region = ConductivityRegion.isotropic([tags['tag_base_endo'], tags['tag_central_endo'], tags['tag_apex_endo']],
                                               'endo', gi, 0.625)
    mid_region = ConductivityRegion.isotropic([tags['tag_base_mid'], tags['tag_central_mid'], tags['tag_apex_mid']],
                                              'mid', gi, 0.625)
    epi_region = ConductivityRegion.isotropic([tags['tag_base_epi'], tags['tag_central_epi'], tags['tag_apex_epi']],
                                              'epi', gi, 0.625)
    g_reg = [endo_region, mid_region, epi_region]
    return g_reg


def setup_stimulus(geom, args):
    """
    Set up stimulus for initiation of propagation
    """
    MM2UM = 1e3
    wedge = geom._size
    wedge_center_um = [0,0,0]#(wedge / 2) * MM2UM
    wedge_um = wedge * MM2UM

    # pad size in um
    pSz = 500

    if args.tm_stim_location == 'endo':
        z = wedge_um[2]/2
    else:
        z = -wedge_um[2]/2

    if args.ab_stim_location == 'apex':
        y = -wedge_um[1]/2
    elif args.ab_stim_location == 'mid':
        y = 0
    else:  # args.ab_stim_location == 'base':
        y = wedge_um[1]/2

    stim = Stimulus('Stim', **{'crct.type': 0,
                               'pulse.strength': 100.0,
                               'ptcl.duration': 1.0,
                               'ptcl.npls': 1,
                               'elec.p0': [wedge_center_um[0]-wedge_um[0]/2,
                                           wedge_center_um[1] + y - pSz,
                                           wedge_center_um[2] + z - pSz],
                               'elec.p1': [wedge_center_um[0]+wedge_um[0]/2,
                                           wedge_center_um[1] + y + pSz,
                                           wedge_center_um[2] + z + pSz]})
    return stim


def setup_lats():
    """
    Simple setup for lat detection based on Vm and threshold crossing
    """
    lat = Lat('LATs', all=0, measurand=0, threshold=-10, method=1)
    return lat


def writeECGgrid(wedge, bath):
    """
    Dynamically generate grid for ECG computations
    We put three recording sites within the tisue along the transmural centerline,
    one intramurally, and two more at endo and epi surface, respectively.
    Furthe, if we have a bath, we put two more in each bath,
    one in the center and another one at the bath boundary.
    """

    # centerline
    xCtr = 0
    yCtr = 0

    # put 3 pts through wedge 
    z_epi = -wedge[2] / 2
    z_ctr = 0
    z_endo = wedge[2] / 2

    if bath == 0.:
        # for phie recovery we set the bath by default to 10 mm
        bath = 10.

    # write a pts file
    pts = np.array([xCtr, yCtr, z_epi])  # tissue points - epi
    pts = np.vstack((pts, [xCtr, yCtr, z_ctr]))  # center
    pts = np.vstack((pts, [xCtr, yCtr, z_endo]))  # endo

    if bath > 0.:
        # put additional pts in each bath
        # epi bath center and boundary
        zbath_epiCtr = z_epi - bath / 2
        zbath_epiSurf = z_epi - bath

        # endo bath center and boundary
        zbath_endoCtr = z_endo + bath / 2
        zbath_endoSurf = z_endo + bath
        # epi bath nodes
        pts = np.vstack((pts, [xCtr, yCtr, zbath_epiSurf]))  # node 3
        pts = np.vstack((pts, [xCtr, yCtr, zbath_epiCtr]))  # node 4
        pts = np.vstack((pts, [xCtr, yCtr, zbath_endoCtr]))  # node 5
        pts = np.vstack((pts, [xCtr, yCtr, zbath_endoSurf]))  # node 6

    pts *= 1e3

    txt.write(os.path.join(CALLER_DIR, 'ecg.pts'), pts)


def compute_tmECG(tmECG, vtx_endo, vtx_epi, job, webgui, idExp):
    """
    Extract endocardial and epicardial unipolar electrograms
    to compute the transmural ECG.
    """

    # extract endo unipolar electrogram
    extract_endo = [settings.execs.igbextract, '-l', vtx_endo,
                                               '-O', os.path.join(tmECG, 'phie_endo.dat'),
                                               '-o', 'ascii',
                                               os.path.join(tmECG, 'phie_recovery.igb')]
    job.bash(extract_endo)


    # extract epi unipolar electrogram
    extract_epi  = [settings.execs.igbextract, '-l', vtx_epi,
                                               '-O', os.path.join(tmECG, 'phie_epi.dat'),
                                               '-o', 'ascii',
                                                os.path.join(tmECG, 'phie_recovery.igb')]
    job.bash(extract_epi)

    # read endo and epi unipolar electrograms
    endo_trace = txt.read(os.path.join(tmECG, 'phie_endo.dat'))
    epi_trace  = txt.read(os.path.join(tmECG, 'phie_epi.dat'))

    tmtrace = endo_trace - epi_trace

    # dump transmural ECG
    txt.write(os.path.join(tmECG, 'tmECG.dat'), tmtrace)

    if (webgui):
        valueX = np.arange(len(tmtrace)).tolist()
        valueY = tmtrace.tolist()
        datadic = {'labels':{'labelsAB':[]},
                   'datasets':{'xlim':[], 'ylim':[],'labelXY':['Time', 'Transmural ECG'],
                               'valueX':valueX, 'valueY1':valueY, 'valueY2':[]}}
        
        with open(idExp + '_' + 'matplotM.txt', 'w') as f:
            for key, value in datadic.items():
                for key2, value2 in value.items():
                    f.write(f'{value2}\n')
    else:

        # plot trace using pyplot
        plt.plot(tmtrace)
        plt.ylabel('Transmural ECG')
        plt.xlabel('Time')
        plt.show()   

if __name__ == '__main__':
    run()    
