%% PlotMaker

language = 'en'

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

if displaycond || displayadm || displayresist
    % Import legends / VS, assuming it is in feuillecond
    [~, ~, raw] = xlsread(xlsname,feuillecond);
    condnames= raw(ligne_offset_cond,2:4)
    condnames(cellfun(@(x) ~isempty(x) && isnumeric(x) && isnan(x),condnames)) = {''};

    % Import the data
    datas_cond = raw(ligne_offset_cond+1:(xsize+ligne_offset_cond),2:4);
    datas_cond = cell2mat(datas_cond);
    % Clear temporary variables
    clearvars raw;
    % Merge with main datas
    datas = horzcat(datas, datas_cond);
    vsnames
    condnames
    vsnames = horzcat(vsnames, condnames);
end

% Absolute-Condorcet IRV
for i=1:length(vsnames)
    if strcmp(vsnames{i},'Absolute-Condorcet IRV')
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
        break
    end
end

% ICRV
for i=1:length(vsnames)
    if strcmp(vsnames{i},'ICRV')
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
        break
    end
end

% C-adm
if ~displayadm
    for i=1:length(vsnames)
        if strcmp(vsnames{i},'not_exists_condorcet_admissible')
            vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
            datas(:,i)=[];
            break
        end
    end
end
% C-win
if ~displaycond
    for i=1:length(vsnames)
        if strcmp(vsnames{i},'not_exists_condorcet_winner')
            vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
            datas(:,i)=[];
            break
        end
    end
end
% C-res
if ~displayresist
    for i=1:length(vsnames)
        if strcmp(vsnames{i},'not_exists_resistant_condorcet_winner')
            vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
            datas(:,i)=[];
            break
        end
    end
end

% Other banned vs
lengthvs = length(vsnames)
for i=lengthvs:-1:1
    i
    vsnames{i}
    any(ismember(voting_systems_banned,vsnames{i}))
    if any(ismember(voting_systems_banned,vsnames{i}))
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
    end
end

% VTB-Condorcet IRV -> Condorcet IRV

% Populate courbes
for i=1:length(vsnames)
    disp(vsnames{i})
    courbes(vsnames{i})={datas(:,i),vsnames{i},markers(vsnames{i}),colors(vsnames{i})}; % y legend marker
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
            if isequal(language,'en')
                toto = 'AV';
            end
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
            if isequal(language,'en')
                toto = 'RV';
            end
        case 'VTB-Condorcet IRV'
            toto='CVTI';
            if isequal(language,'en')
                toto = 'CIRV';
            end
        case 'Majority Judgment'
            toto='JM';
            if isequal(language,'en')
                toto = 'MJ';
            end
        case 'Plurality'
            toto='Uni.';
            if isequal(language,'en')
                toto = 'Plu.';
            end
        case 'Kemeny'
            toto='Kem.';
        case 'Maximin'
            toto='Max.';
        case 'Nanson'
            toto='Nan.';
        case 'Exhaustive Ballot'
            toto='SE';
            if isequal(language,'en')
                toto = 'EB';
            end
        case 'Iterated Bucklin'
            toto='BI';
            if isequal(language,'en')
                toto = 'IB';
            end
        case 'Schulze'
            toto='Sch.';
        case 'Two Round'
            toto='U2T';
            if isequal(language,'en')
                toto = 'TR';
            end
        case 'IRV'
            toto='VTI';
            if isequal(language,'en')
                toto = 'IRV';
            end
        case 'IRV Duels'
            toto='VTID';
            if isequal(language,'en')
                toto = 'IRVD';
            end
        case 'Ranked Pairs'
            toto='PO';
            if isequal(language,'en')
                toto = 'RP';
            end
        case 'Condorcet Sum Defeats'
            toto='CSD';
        case 'not_exists_condorcet_admissible'
            toto='Non Adm.';
            if isequal(language,'en')
                toto = 'Non-Adm.';
            end
        case 'not_exists_condorcet_winner'
            toto='Non Cond.';
            if isequal(language,'en')
                toto = 'Non-Cond.';
            end
        case 'not_exists_resistant_condorcet_winner'
            toto='Non Res.';
            if isequal(language,'en')
                toto = 'Non-Res.';
            end
        otherwise
            toto = vsnames{i};
    end
    switch vsnames{i}
        case 'not_exists_condorcet_admissible'
            lege{i}=toto;
        case 'not_exists_condorcet_winner'
            lege{i}=toto;
        case 'not_exists_resistant_condorcet_winner'
            lege{i}=toto;
        otherwise
        %     if incert(vsnames{i})>0.005
        %         lege{i}=[toto ' (\epsilon = ' num2str(round(100*incert(vsnames{i}))) '%)'];
        %     else
        %         lege{i}=toto;
        %     end
            if incert(vsnames{i})>=0.015
                lege{i}=[toto ' *'];
            else
                lege{i}=toto;
            end
    end
end


%% Plot
clf
h=figure(1);
for i=1:length(vsnames)
    courbe=courbes(vsnames{i}); % y legend marker
    myplot(xx,courbe{1},courbe{3},'color',courbe{4},'linewidth',1,'markersize',8)
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
% tata=2.^(-3:3);
set(gca,'XTick',x_ticks); % Change x-axis ticks
set(gca,'XTickLabel',x_ticks_labels); % Change x-axis ticks labels to desired values.
xlim([min(xx) max(xx)])
ylim([0 1])
y_ticks_labels = {'0 %', '10 %', '20 %', '30 %', '40 %', '50 %', ...
    '60 %', '70 %', '80 %', '90 %', '100 %'};
set(gca,'YTickLabel',y_ticks_labels);
set(gcf, 'PaperPositionMode', 'auto');
% set(gcf, 'PaperUnits', 'inches');
% set(gcf, 'PaperPosition', [.25 .25 12 8]);

set(h, 'Position', figsize)

if isequal(language,'en')
    fname = [fname '_en'];
end

print(h,'-depsc2',fname)
print(h,'-djpeg',fname)
