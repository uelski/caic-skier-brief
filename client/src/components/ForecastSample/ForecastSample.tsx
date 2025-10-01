import { Box, Text } from "@mantine/core";
import type { Forecast } from "../../types";
import { DangerLevels } from "../DangerLevels/DangerLevels";

export function ForecastSample({ forecast }: { forecast: Forecast }) {
    return (
        <Box>
            <Text c="white">{forecast.summary}</Text>
            <DangerLevels levels={forecast.levels} />
        </Box>
    );
}