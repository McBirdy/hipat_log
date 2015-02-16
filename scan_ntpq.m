clear
% Import files
files = dir('*.txt');

A = zeros(1,length(files));

for i=1:length(files)
    pid = fopen(files(i).name);
    rawdata = textscan(pid, '%s %s %f %f');
    fclose(pid);
    
    date = rawdata{1}(:);
    time = rawdata{2}(:);
    offset = rawdata{3}(:);
    jitter = rawdata{4}(:);

    date = strcat(date, '_');
    date = strcat(date, time);

    date_time = datenum(date,'yyyy-mm-dd_HH:MM:SS');
    
    A(i) = subplot(length(files),1,i);
    plot(date_time, offset);
    title(files(i).name);
    dynamicDateTicks();
    

end

linkaxes([A], 'xy');