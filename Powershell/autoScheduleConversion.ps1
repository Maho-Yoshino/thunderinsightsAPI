cd "C:\Users\djandDK\Documents\Code\WtTools.Unpacker"

# Get write times of files and compare them to see if it has changed
$lastupdate = Get-Content C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\progress.txt
$currentupdateChar = ([DateTimeOffset](Get-ChildItem C:\Users\djandDK\AppData\Local\WarThunder\char.vromfs.bin).LastWriteTime).ToUnixTimeSeconds()

if($currentupdateChar -gt $lastupdate) {

    # Copy file from war thunder folder
    cp C:\Users\djandDK\AppData\Local\WarThunder\char.vromfs.bin C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder -Force

    # Decode file
    C:\Users\djandDK\Documents\Code\WtTools.Unpacker\WtTools.Unpacker.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder

    # move file to truenas
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\char.vromfs.bin_u\config\wpcost.blkx \\192.168.3.1\DockerData\PythonCron\dailyInfoUpdate\wpcost.json -Force
	# cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\char.vromfs.bin_u\config\unittags.blkx \\192.168.3.1\DockerData\PythonCron\dailyInfoUpdate\unittags.json -Force

    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\char.vromfs.bin_u\config\wpcost.blkx \\192.168.3.1\DockerData\Celery\app\gamefiles\wpcost.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\char.vromfs.bin_u\config\unittags.blkx \\192.168.3.1\DockerData\Celery\app\gamefiles\unittags.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\char.vromfs.bin_u\config\rank.blkx \\192.168.3.1\DockerData\Celery\app\gamefiles\rank.json -Force

    # Update when the file was last written to
    $currentupdateChar | Set-Content C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\progress.txt -Force
}

# Check the update time for the images folder
$currentupdateImages = ([DateTimeOffset](Get-ChildItem C:\Users\djandDK\AppData\Local\WarThunder\ui\images.vromfs.bin).LastWriteTime).ToUnixTimeSeconds()

if($currentupdateImages -gt $lastupdate) {
    # Copy file from war thunder folder
    cp C:\Users\djandDK\AppData\Local\WarThunder\ui\images.vromfs.bin C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder -Force

    # Decode file
    C:\Users\djandDK\Documents\Code\warthunder.Unpacker.Python\vromfs_unpacker.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin

    # move files to truenas nonprod
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\avatars\* \\192.168.3.1\DockerData\Nginx\config\www\images\avatars -Force -recurse
	# cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\flags\unit_tooltip\* \\192.168.3.1\DockerData\Nginx\config\www\images\flags -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\avatars\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\avatars -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\flags\unit_tooltip\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\flags -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\avatar_frames\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\avatars\frames -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\profile_headers\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\profile\headers -Force -recurse

	# move files to truenas prod
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\avatars\* \\192.168.3.1\DockerData\NginxProduction\config\www\images\avatars -Force -recurse
	# cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\flags\unit_tooltip\* \\192.168.3.1\DockerData\NginxProduction\config\www\images\flags -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\avatars\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\avatars -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\flags\unit_tooltip\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\flags -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\avatar_frames\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\avatars\frames -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\images.vromfs.bin_u\images\profile_headers\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\profile\headers -Force -recurse

    # Update when the file was last written to if it's greater than the char file
    if ($currentupdateImages -gt $currentupdateChar) {
        $currentupdateImages | Set-Content C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\progress.txt -Force
    }
}

# Check the update time for the images folder
$currentupdateTex = ([DateTimeOffset](Get-ChildItem C:\Users\djandDK\AppData\Local\WarThunder\ui\tex.vromfs.bin).LastWriteTime).ToUnixTimeSeconds()

if($currentupdateTex -gt $lastupdate) {
    # Copy file from war thunder folder
    cp C:\Users\djandDK\AppData\Local\WarThunder\ui\tex.vromfs.bin C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder -Force

    # Decode file
    C:\Users\djandDK\Documents\Code\warthunder.Unpacker.Python\vromfs_unpacker.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin

    # move files to truenas nonprod
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\aircrafts\* \\192.168.3.1\DockerData\Nginx\config\www\images\vehicles -Force -recurse
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\ships\* \\192.168.3.1\DockerData\Nginx\config\www\images\vehicles -Force -recurse
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\tanks\* \\192.168.3.1\DockerData\Nginx\config\www\images\vehicles -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\aircrafts\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\units -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\ships\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\units -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\tanks\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\units -Force -recurse
	
	# move files to truenas prod
	# cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\aircrafts\* \\192.168.3.1\DockerData\NginxProduction\config\www\images\vehicles -Force -recurse
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\ships\* \\192.168.3.1\DockerData\NginxProduction\config\www\images\vehicles -Force -recurse
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\tanks\* \\192.168.3.1\DockerData\NginxProduction\config\www\images\vehicles -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\aircrafts\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\units -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\tanks\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\units -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\tex.vromfs.bin_u\tanks\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\units -Force -recurse

    # Update when the file was last written to if it's greater than the char file
    if ($currentupdateTex -gt $currentupdateChar -and $currentupdateTex -gt $currentupdateImages) {
        $currentupdateTex | Set-Content C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\progress.txt -Force
    }
}

# Check the update time for the images folder
$currentupdateLang = ([DateTimeOffset](Get-ChildItem C:\Users\djandDK\AppData\Local\WarThunder\lang.vromfs.bin).LastWriteTime).ToUnixTimeSeconds()

if($currentupdateLang -gt $lastupdate) {
    # Copy file from war thunder folder
    cp C:\Users\djandDK\AppData\Local\WarThunder\lang.vromfs.bin C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder -Force

    # Decode file
    C:\Users\djandDK\Documents\Code\warthunder.Unpacker.Python\vromfs_unpacker.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin

    # Convert from CSV to JSON
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\units.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\units.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_achievements.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_achievements.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\menu_options.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\menu_options.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\_common_languages.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\_common_languages.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_conditions.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_conditions.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\menu.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\menu.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_medals.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_medals.json
    (Import-CSV C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_challenges.csv -Delimiter ";" | ConvertTo-Json -depth 100).replace("\u003c","").replace("\u003e","").replace("|readonly|noverify","") | Out-File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_challenges.json

    # move files to truenas
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\units.json \\192.168.3.1\DockerData\PythonCron\dailyInfoUpdate\units.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\units.json \\192.168.3.1\DockerData\Celery\app\gamefiles\units.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_achievements.json \\192.168.3.1\DockerData\Celery\app\gamefiles\unlocks_achievements.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\menu_options.json \\192.168.3.1\DockerData\Celery\app\gamefiles\menu_options.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\_common_languages.json \\192.168.3.1\DockerData\Celery\app\gamefiles\_common_languages.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_conditions.json \\192.168.3.1\DockerData\Celery\app\gamefiles\unlocks_conditions.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\menu.json \\192.168.3.1\DockerData\Celery\app\gamefiles\menu.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_medals.json \\192.168.3.1\DockerData\Celery\app\gamefiles\unlocks_medals.json -Force
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\lang.vromfs.bin_u\lang\unlocks_challenges.json \\192.168.3.1\DockerData\Celery\app\gamefiles\unlocks_challenges.json -Force

    
    # Update when the file was last written to if it's greater than the char file
    if ($currentupdateLang -gt $currentupdateChar -and $currentupdateLang -gt $currentupdateImages -and $currentupdateLang -gt $currentupdateTex) {
        $currentupdateLang | Set-Content C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\progress.txt -Force
    }
}

# Check the update time for the images folder
$currentupdateAtlas = ([DateTimeOffset](Get-ChildItem C:\Users\djandDK\AppData\Local\WarThunder\ui\atlases.vromfs.bin).LastWriteTime).ToUnixTimeSeconds()

if($currentupdateAtlas -gt $lastupdate) {
    # Copy file from war thunder folder
    cp C:\Users\djandDK\AppData\Local\WarThunder\ui\atlases.vromfs.bin C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder -Force

    # Decode file
    C:\Users\djandDK\Documents\Code\warthunder.Unpacker.Python\vromfs_unpacker.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin

    # Unpack DDSX files into DDS
    C:\Users\djandDK\Documents\Code\warthunder.Unpacker.Python\ddsx_unpack.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\medals
    C:\Users\djandDK\Documents\Code\warthunder.Unpacker.Python\ddsx_unpack.exe C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\units

    # Convert from DDS to PNG
    Get-ChildItem C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\medals | Where-Object Extension -eq ".dds" | ForEach-Object {powershell -ExecutionPolicy Bypass -File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\ConvertTo-Png.ps1 $_.FullName}
    Get-ChildItem C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\units | Where-Object Extension -eq ".dds" | ForEach-Object {powershell -ExecutionPolicy Bypass -File C:\Users\djandDK\Documents\Code\WtTools.Unpacker\ConvertTo-Png.ps1 $_.FullName}

    # move files to truenas nonprod
    # cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\gameuiskin\* \\192.168.3.1\DockerData\Nginx\config\www\images\uiElements -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\gameuiskin\* \\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\uielements -Force -recurse
    Get-ChildItem C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\medals | Where-Object Extension -eq ".png" | ForEach-Object {cp $_.FullName "\\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\medals\$($_.Name)" -Force}
    Get-ChildItem C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\units | Where-Object Extension -eq ".png" | ForEach-Object {cp $_.FullName "\\192.168.3.1\DockerData\FastAPIWarThunderDev\app\static\units\small\$($_.Name)" -Force}
	
	# move files to truenas prod
	# cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\gameuiskin\* \\192.168.3.1\DockerData\NginxProduction\config\www\images\uiElements -Force -recurse
    cp C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\gameuiskin\* \\192.168.3.1\DockerData\FastAPIWarThunder\app\static\uielements -Force -recurse
    Get-ChildItem C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\medals | Where-Object Extension -eq ".png" | ForEach-Object {cp $_.FullName "\\192.168.3.1\DockerData\FastAPIWarThunder\app\static\medals\$($_.Name)" -Force}
    Get-ChildItem C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\atlases.vromfs.bin_u\units | Where-Object Extension -eq ".png" | ForEach-Object {cp $_.FullName "\\192.168.3.1\DockerData\FastAPIWarThunder\app\static\units\small\$($_.Name)" -Force}

    # Update when the file was last written to if it's greater than the char file
    if ($currentupdateAtlas -gt $currentupdateLang -and $currentupdateAtlas -gt $currentupdateChar -and $currentupdateAtlas -gt $currentupdateImages -and $currentupdateAtlas -gt $currentupdateTex) {
        $currentupdateAtlas | Set-Content C:\Users\djandDK\Documents\Code\WtTools.Unpacker\conversionFolder\progress.txt -Force
    }
}