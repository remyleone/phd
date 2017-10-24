%% Universal Legend
markers=containers.Map;
vs={'Approval','Range voting with average','Majority Judgment',...
    'Borda','Veto','Plurality',...
    'Condorcet Sum Defeats','Kemeny','Maximin','Baldwin',...
    'Nanson','Ranked Pairs','Schulze',...
    'Exhaustive Ballot','IRV','ICRV','VTB-Condorcet IRV',...
    'Absolute-Condorcet IRV','IRV Duels',...
    'Iterated Bucklin','Bucklin','Coombs','Two Round'};
m = {'md-','md:','md-.'...
    'go-','go:','go-.',...
    'k^-','k^:','k^-.','k^--',...
    'kv-','kv:','kv-.'...
    'b+-','b+:','b+-.','b+--',...
    'bx:','bx-',...
    'r-','r:','r-.','r--'};
for i=1:length(vs)
    markers(vs{i})=m{i};
end

%% Default value

feuille='Feuil1';
feuilleincert='Incertitude';
myplot=@plot;
ligne_offset=4;


%% Gaussian 1D variables

xlsname='Results_2014-11-16_13-16-36_m_fr_gaussian1d_shift.xls';
fname='gaussian1dshift';
xl='Shift';
yl='CM rate';

loc='northeast';
figsize=[100 100 600 450];
xsize=11;

run('plotmaker')


%% Gaussian XD

xlsname='Results_2014-11-14_22-32-35_m_fr_gaussian_xd.xls';
fname='gaussianxd';
xl='Number of dimensions d';
yl='CM rate';

xsize=10;

run('plotmaker')


%% Gaussian 2D

xlsname='Results_2014-11-16_13-18-07_m_fr_gaussian2d_ratio.xls';
fname='gaussian2d';
xl='\sigma_2';
yl='CM rate';

xsize=11;

run('plotmaker')

%% VMF Concentration

xlsname='Results_2014-11-16_13-23-13_m_fr_VMF_concentration.xls';
fname='vmfconcentration';
xl='Concentration \lambda';
yl='CM rate';

xsize=13;

run('plotmaker')

%% VMF number of poles

xlsname='Results_2014-11-16_13-25-08_m_fr_VMF_number_of_poles.xls';
fname='vmfnumberpole';
xl='Number of poles';
yl='CM rate';

loc='northeast';
xsize=16;

run('plotmaker')

%% VMF Position of pole

xlsname='Results_2014-11-14_23-33-34_m_fr_VMF_position_pole.xls';
fname='vmfpoleposition';
xl='Relative position of pole \theta / \theta_{max}';
yl='CM rate';

loc='northwest';
xsize=13;

feuilleincert='Feuil2';
run('plotmaker')
feuilleincert='Incertitude';

%% VMF angle

xlsname='Results_2014-11-16_13-27-11_m_fr_VMF_angle_between_poles.xls';
fname='vmfangle';
xl='Relative angle between poles 2\theta/\pi';
yl='CM rate';


xsize=13;

run('plotmaker')

%% Gaussian1d V big

xlsname='Results_2014-11-14_22-03-02_m_fr_gaussian1d_V.xls';
fname='gaussian1dvbig';
xl='V';
yl='CM rate';

feuille='Feuil2';
loc='northeast';
figsize=[100 100 600 450];
ligne_offset=1;
xsize=26;

myplot=@semilogx;

run('plotmaker')


%% Gaussian1d V small

xlsname='Results_2014-11-14_22-03-02_m_fr_gaussian1d_V.xls';
fname='gaussian1dvsmall';
xl='V';
yl='CM rate';
feuille='Feuil1';

myplot=@plot;

ligne_offset=5;
xsize=31;

run('plotmaker')

%% Sphere V big

xlsname='Results_2014-11-14_22-54-39_m_fr_sphere_V.xls';
fname='spherevbig';
xl='V';
yl='CM rate';

feuille='Feuil2';
ligne_offset=1;
xsize=21;

myplot=@semilogx;

run('plotmaker')


%% Sphere V small

xlsname='Results_2014-11-14_22-54-39_m_fr_sphere_V.xls';
fname='spherevsmall';
xl='V';
yl='CM rate';
feuille='Feuil1';

myplot=@plot;

ligne_offset=5;
xsize=31;

run('plotmaker')

%% Euclidian V big

xlsname='Results_2014-11-14_22-33-28_m_fr_euclidean1d_V.xls';
fname='euclidianvbig';
xl='V';
yl='CM rate';

feuille='Feuil2';
ligne_offset=1;
xsize=21;

myplot=@semilogx;

run('plotmaker')


%% Euclidian V small

xlsname='Results_2014-11-14_22-33-28_m_fr_euclidean1d_V.xls';
fname='euclidianvsmall';
xl='V';
yl='CM rate';
feuille='Feuil1';

myplot=@plot;

ligne_offset=5;
xsize=31;

run('plotmaker')

%% GaussianC

xlsname='Results_2014-11-14_m_fr_gaussian1d_C.xls';
fname='gaussianc';
xl='C';
yl='CM rate';

figsize=[100 100 1200 600];
ligne_offset=4;
xsize=13;
feuilleincert='Feuil2';

run('plotmaker')
feuilleincert='Incertitude';

%% SphereC

xlsname='Results_2014-11-14_m_fr_sphere_C.xls';
fname='spherec';
xl='C';
yl='CM rate';

figsize=[100 100 1200 600];
ligne_offset=4;
xsize=13;
loc='southeast';

run('plotmaker')
