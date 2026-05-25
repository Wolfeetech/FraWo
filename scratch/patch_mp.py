with open('/tmp/MediaProcessor.php', 'r') as f:
    content = f.read()

# Replace the catch block in __invoke()
old_str = 'catch (CannotProcessMediaException $e) {'
new_str = 'catch (\\Throwable $e) {'

if old_str in content:
    content = content.replace(old_str, new_str)
    print("Successfully replaced catch block!")
else:
    print("Error: Target string not found in file!")

with open('/tmp/MediaProcessor.php', 'w') as f:
    f.write(content)
