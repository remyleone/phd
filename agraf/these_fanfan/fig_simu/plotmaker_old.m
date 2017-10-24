%% PlotMaker

%% Importing
courbes=containers.Map;
% Import legends / VS, assuming it is in Feuil1
[~, ~, raw] = xlsread(xlsname,feuille);
vsnames= raw(ligne_offset,2:24);
vsnames(cellfun(@(x) ~isempty(x) && isnumeric(x) && isnan(x),vsnames)) = {''};

% Import the data
datas = raw(ligne_offset+1:(xsize+ligne_offset),2:24);
datas = cell2mat(datas);
xx = raw(ligne_offset+1:(xsize+ligne_offset),1);
xx = cell2mat(xx);
% xx=xx/12;
% Clear temporary variables
clearvars raw;

for i=1:length(vsnames)
    if strcmp(vsnames{i},'Absolute-Condorcet IRV')
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
        break
    end
end
% Absolute-Condorcet IRV

for i=1:length(vsnames)
    if strcmp(vsnames{i},'ICRV')
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
        break
    end
end
% ICRV

% VTB-Condorcet IRV -> Condorcet IRV

% Populate courbes
for i=1:length(vsnames)
    disp(vsnames{i})
    courbes(vsnames{i})={datas(:,i),vsnames{i},markers(vsnames{i})}; % y legend marker
end

% Incertitudes
[~, ~, raw] = xlsread(xlsname,feuilleincert);
cles = raw(5:27,1);
cles(cellfun(@(x) ~isempty(x) && isnumeric(x) && isnan(x),cles)) = {''};
vals = raw(5:27,2);
vals=  cell2mat(vals);
incert=containers.Map;
for i=1:length(cles)
    incert(cles{i})=vals(i);
end

%% Creating legends
lege={};
for i=1:length(vsnames)
    switch vsnames{i}
        case 'Approval'
            toto='VA';
        case 'Baldwin'
            toto='Bald.';
        case 'Borda'
            toto='Bor.';
        case 'Bucklin'
            toto='Buck.';
        case 'Coombs'
            toto='Coo.';
        case 'Range voting with average'
            toto='VN';
        case 'VTB-Condorcet IRV'
            toto='CVTI';
        case 'Majority Judgment'
            toto='JM';
        case 'Plurality'
            toto='Uni.';
        case 'Kemeny'
            toto='Kem.';
        case 'Maximin'
            toto='Max.';
        case 'Nanson'
            toto='Nan.';
        case 'Exhaustive Ballot'
            toto='SE';
        case 'Iterated Bucklin'
            toto='BI';
        case 'Schulze'
            toto='Sch.';
        case 'Two Round'
            toto='U2T';
        case 'IRV Duels'
            toto='VTID';
        case 'Ranked Pairs'
            toto='PO';
        case 'Condorcet Sum Defeats'
            toto='CSD';
        otherwise
            toto = vsnames{i};
    end
%     if incert(vsnames{i})>0.005
%         lege{i}=[toto ' (\epsilon = ' num2str(round(100*incert(vsnames{i}))) '%)'];
%     else
%         lege{i}=toto;
%     end
    if incert(vsnames{i})>0.01
        lege{i}=[toto '*'];
    else
        lege{i}=toto;
    end
end


%% Plot
clf
h=figure(1);
for i=1:length(vsnames)
    courbe=courbes(vsnames{i}); % y legend marker
    myplot(xx,courbe{1},courbe{3},'linewidth',1,'markersize',8)
    hold on
end
hold off
l=legend(lege,'Location',loc,'fontsize',8);
%set(h,'Location',get)
xlabel(xl)
ylabel(yl)
% Pole position trick
% tata=0:3:12;
% set(gca,'XTick',tata); % Change x-axis ticks
% set(gca,'XTickLabel',0:.25:1); % Change x-axis ticks labels to desired values.
% tata=2.^(1:10)+1;
% set(gca,'XTick',tata); % Change x-axis ticks
% set(gca,'XTickLabel',tata); % Change x-axis ticks labels to desired values.
xlim([,min(xx) max(xx)])
set(gcf, 'PaperPositionMode', 'auto');
% set(gcf, 'PaperUnits', 'inches');
% set(gcf, 'PaperPosition', [.25 .25 12 8]);

set(h, 'Position', figsize)


print(h,'-depsc2',fname)
print(h,'-djpeg',fname)
