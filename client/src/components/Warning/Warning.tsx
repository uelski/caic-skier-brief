import { Box, Text, Title } from "@mantine/core";

export function Warning() { 
    return (
        <Box bg="rgb(176, 3, 9)" p="sm" ta="center" mb="lg">
            <Title mb="xs" fz="xl" c="white">IMPORTANT WARNING!</Title>
            <Text c="white" fw="bold">THIS SITE IS FOR DEMO PURPOSES ONLY AND SHOULD NOT BE USED TO PLAN ANY BACKCOUNTRY ACTIVITIES. ALWAYS GET THE FORECAST AT THE OFFICIAL SOURCE: <span><a style={{ color: 'white' }} href="https://avalanche.state.co.us/" target="_blank">CAIC</a></span></Text>
        </Box>
    );
}