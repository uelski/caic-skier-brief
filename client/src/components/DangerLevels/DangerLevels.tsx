import type { ElevBand, DangerLevel } from '../../types';
import { Box, Title, Text } from '@mantine/core';

export function DangerLevels({ levels }: { levels: Record<ElevBand, DangerLevel> }) {
    return (
        <Box>
            <Title>Danger Levels</Title>
            {
                Object.entries(levels).map(([elevBand, dangerLevel]) => (
                    <Text key={elevBand}>{elevBand}: {dangerLevel}</Text>
                ))
            }
        </Box>
    );
}   